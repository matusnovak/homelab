package controllers

import (
	"context"
	"database/sql"
	errs "errors"
	"fmt"
	"github.com/go-logr/logr"
	_ "github.com/lib/pq"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/types"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

func FindService(c client.Client, logger logr.Logger, namespace string, name string) (*corev1.Service, error) {
	postgres := &corev1.Service{}
	err := c.Get(context.TODO(), types.NamespacedName{Namespace: namespace, Name: name}, postgres)
	if err != nil {
		return nil, errs.New(fmt.Sprintf("Unable to find service: %s in namespace: %s error: %s", name, namespace, err))
	}

	logger.Info(fmt.Sprintf("Found service: %s for namespace: %s", name, namespace))

	return postgres, nil
}

func FindPodsForService(c client.Client, logger logr.Logger, service *corev1.Service) ([]corev1.Pod, error) {
	pods := &corev1.PodList{}
	err := c.List(context.TODO(), pods, client.InNamespace(service.Namespace))
	if err != nil {
		return nil, errs.New(fmt.Sprintf("unable to list pods in namespace: %s error: %s", service.Namespace, err))
	}

	logger.Info(fmt.Sprintf("Found %d pods for namespace %s", len(pods.Items), service.Namespace))

	selector := service.Spec.Selector

	var found []corev1.Pod

	for _, pod := range pods.Items {
		labels := pod.Labels

		selected := true

		for key, label := range selector {
			if _, ok := labels[key]; ok {
				if labels[key] != label {
					selected = false
					break
				}
			} else {
				selected = false
				break
			}
		}

		if selected {
			found = append(found, pod)
		}
	}

	if len(found) == 0 {
		return nil, errs.New(fmt.Sprintf("No pods found for service: %s namespace: %s", service.Name, service.Namespace))
	}

	logger.Info(fmt.Sprintf("Found %d pods matching service: %s namespace %s", len(found), service.Name, service.Namespace))

	return found, nil
}

func findInEnv(env []corev1.EnvVar, name string) (string, error) {
	for _, e := range env {
		if e.Name == name {
			return e.Value, nil
		}
	}
	return "", errs.New(fmt.Sprintf("Pod has no such environment key: %s", name))
}

func GetPostgresConnection(client client.Client, logger logr.Logger, namespace string) (*sql.DB, error) {
	service, err := FindService(client, logger, namespace, "postgres")
	if err != nil {
		return nil, err
	}

	pods, err := FindPodsForService(client, logger, service)
	if err != nil {
		return nil, err
	}

	if len(pods[0].Spec.Containers) == 0 {
		return nil, errs.New(fmt.Sprintf("No containers found for pods for service: %s namespace: %s", service.Name, service.Namespace))
	}

	env := pods[0].Spec.Containers[0].Env
	pgUser, err := findInEnv(env, "POSTGRES_USER")
	if err != nil {
		return nil, err
	}

	pgDatabase, err := findInEnv(env, "POSTGRES_DB")
	if err != nil {
		return nil, err
	}

	pgPassword, err := findInEnv(env, "POSTGRES_PASSWORD")
	if err != nil {
		return nil, err
	}

	pgUrl := fmt.Sprintf("%s.%s.svc.cluster.local:5432", service.Name, service.Namespace)

	logger.Info(fmt.Sprintf("Creating new DB connection to: %s", pgUrl))

	connStr := fmt.Sprintf("postgres://%s:%s@%s/%s?sslmode=disable", pgUser, pgPassword, pgUrl, pgDatabase)
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, err
	}

	return db, nil
}
