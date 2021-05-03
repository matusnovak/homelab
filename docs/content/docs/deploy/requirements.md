---
weight: 1
title: "Requirements"
---

# Deploy - Requirements

## OS

It is recommended that you will use Ubuntu or similar Debian based system. This project assumes that you have `apt-get` installed. It is highly recommended that you use [Ubuntu Server](https://ubuntu.com/download/server) for the best experience.

## Docker

This project requires that you have installed Docker. Link to the instructions: https://docs.docker.com/engine/install/ubuntu/

You don't need to install Docker compose.

## Python 3

You will need to install Python 3 and pip. The Python 3 already comes installed with the latest Ubuntu OS by default. To install Python and pip, use the following command:

```bash
$ sudo apt-get install python3 python3-pip
```

## Ansible

Finally, you will need Ansible installed on your machine where you are running this project from. Link to the instructions: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-on-ubuntu

In short, you will have to do the following:

```bash
$ sudo apt update
$ sudo apt install software-properties-common
$ sudo apt-add-repository --yes --update ppa:ansible/ansible
$ sudo apt install ansible
```

## Swarm Mode

You must setup Docker Swarm. You don't need to add additional nodes into your cluster (but you can). All you need is a single manager. To configure Docker in Swarm Mode, run the following command:

```bash
$ docker swarm init
```

You don't need to do additional steps afterwards. The token displayed in the output is used to connect additional worker nodes into your manager.

## Next

**[Folder Structure]({{< ref "folder_structure.md" >}})**
