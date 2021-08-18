from ansible.module_utils.basic import AnsibleModule
import docker
import json
import requests
import sys

# 1. Download (pull) image from "image" parameter
# 2. Tag it with "address" parameter
# 3. Push it into "address"


def extract_image_and_tag(name: str):
    # example: "registry.example.com:5000/library/image:tag"
    # turns into: ["registry.example.com:5000", "library/image", "tag"]

    name_parts = name.split('/')
    tag_parts = name_parts[-1].split(':')

    if len(name_parts) == 1:
        name_parts = ['library', name_parts[0]]

    if len(name_parts) == 2:
        name_parts = ['docker.io'] + name_parts

    if len(tag_parts) == 1:
        tag = 'latest'
        name = tag_parts[0]
    else:
        tag = tag_parts[-1]
        name = ''.join(tag_parts[:-1])

    return (name_parts[0], '/'.join(name_parts[1:-1]) + '/' + name, tag)


def check_if_exists_local(client, image: str):
    local_images = client.images.list()
    for local_image in local_images:
        for repo_tag in local_image.attrs['RepoTags']:
            full_name = repo_tag
            if '/' not in full_name:
                full_name = 'library/' + full_name

            if len(full_name.split('/')) == 2:
                full_name = 'docker.io/' + full_name

            if full_name == image:
                return local_image
    return None


def check_if_exists_remote(address: str, image_name: str, tag: str):
    url = f'http://{address}/v2/_catalog'
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f'{url} returned {r.status_code}')

    found = False
    images = r.json()['repositories']

    for name in images:
        if name == image_name:
            found = True
            break

    if not found:
        return False

    url = f'http://{address}/v2/{image_name}/tags/list'
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f'{url} returned {r.status_code}')

    tags = r.json()['tags']
    for t in tags:
        if t == tag:
            return True
    return False


def main():
    module_args = {
        'image': {
            'type': 'str',
            'required': True
        },
        'address': {
            'type': 'str',
            'required': True
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    client = docker.from_env()

    address = module.params['address']
    image_repo, image_name, image_tag = extract_image_and_tag(
        module.params['image'])
    image_full_name = f'{image_repo}/{image_name}:{image_tag}'

    registry_image_name = f'{address}/{image_name}'
    registry_image_name_with_tag = f'{registry_image_name}:{image_tag}'

    if check_if_exists_remote(address, image_name, image_tag):
        module.exit_json(msg='Success', name=registry_image_name_with_tag)
        return

    local_image = check_if_exists_local(client, image_full_name)
    already_exists = False

    if local_image is None:
        #print(f'Pulling image {image_full_name}')
        local_image = client.images.pull(image_full_name)
    else:
        #print(f'Image already exists on local!')
        already_exists = True

    local_image.tag(registry_image_name, tag=image_tag)

    #print(f'Pushing {registry_image_name}:{image_tag}')
    for line in client.images.push(registry_image_name, tag=image_tag, stream=True, decode=True):
        if 'error' in line and line['error']:
            module.exit_json(failed=True, msg=line['errorDetail'])
        # print(line)

    # Cleanup
    client.images.remove(registry_image_name_with_tag)
    if not already_exists:
        client.images.remove(local_image.id)

    module.exit_json(msg='Success', name=registry_image_name_with_tag)


if __name__ == '__main__':
    main()
