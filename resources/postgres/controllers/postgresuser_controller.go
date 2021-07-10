/*
Copyright 2021.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package controllers

import (
	"context"
	"database/sql"
	"fmt"
	"k8s.io/client-go/tools/record"
	"sigs.k8s.io/controller-runtime/pkg/reconcile"

	"k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	postgresv1 "github.com/matusnovak/homelab/resources/postgres/api/v1"
)

// PostgresUserReconciler reconciles a PostgresUser object
type PostgresUserReconciler struct {
	client.Client
	Scheme   *runtime.Scheme
	Recorder record.EventRecorder
}

//+kubebuilder:rbac:groups=postgres.matusnovak.com,resources=postgresusers,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=postgres.matusnovak.com,resources=postgresusers/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=postgres.matusnovak.com,resources=postgresusers/finalizers,verbs=update

func pgUserExists(db *sql.DB, name string) (bool, error) {
	rows, err := db.Query("SELECT rolname FROM pg_catalog.pg_roles")
	if err != nil {
		return false, err
	}

	defer rows.Close()

	for rows.Next() {
		var rolename string
		err = rows.Scan(&rolename)

		if err != nil {
			return false, err
		}

		if rolename == name {
			return true, nil
		}
	}

	return false, nil
}

func pgUserCreate(db *sql.DB, name string, password string, superuser bool) error {
	_, err := db.Exec(fmt.Sprintf("CREATE ROLE %s", name))
	if err != nil {
		return err
	}

	_, err = db.Exec(fmt.Sprintf("ALTER ROLE %s WITH PASSWORD '%s'", name, password))
	if err != nil {
		return err
	}

	_, err = db.Exec(fmt.Sprintf("ALTER ROLE %s WITH LOGIN", name))
	if err != nil {
		return err
	}

	if superuser {
		_, err = db.Exec(fmt.Sprintf("ALTER ROLE %s WITH SUPERUSER", name))
		if err != nil {
			return err
		}
	}

	return nil
}

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
// TODO(user): Modify the Reconcile function to compare the state specified by
// the PostgresUser object against the actual cluster state, and then
// perform operations to make the cluster state reflect the state specified by
// the user.
//
// For more details, check Reconcile and its Result here:
// - https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.8.3/pkg/reconcile
func (r *PostgresUserReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := log.FromContext(ctx)

	instance := &postgresv1.PostgresUser{}
	err := r.Get(context.TODO(), req.NamespacedName, instance)
	if err != nil {
		if errors.IsNotFound(err) {
			// Object not found, return.  Created objects are automatically garbage collected.
			// For additional cleanup logic use finalizers.
			return reconcile.Result{}, nil
		}
		// error reading the object, requeue the request
		return ctrl.Result{}, err
	}

	db, err := GetPostgresConnection(r.Client, logger, req.Namespace)
	if err != nil {
		logger.Error(err, "Failed to get PostgreSQL connection")
		r.Recorder.Event(instance, "Error", "Failed", err.Error())
		return ctrl.Result{}, err
	}
	defer db.Close()

	logger.Info(fmt.Sprintf("Checking for PostgreSQL user: %s", instance.Spec.Name))

	exists, err := pgUserExists(db, instance.Spec.Name)
	if err != nil {
		logger.Error(err, "Failed to check if user exists")
		r.Recorder.Event(instance, "Error", "Failed", err.Error())
		return ctrl.Result{}, err
	}

	if exists {
		r.Recorder.Event(instance, "Normal", "Created", "PostgreSQL user already exists")
		return ctrl.Result{}, nil
	}

	logger.Info(fmt.Sprintf("Creating new PostgreSQL user: %s", instance.Spec.Name))

	err = pgUserCreate(db, instance.Spec.Name, instance.Spec.Password, instance.Spec.Superuser)
	if err != nil {
		logger.Error(err, "Failed to create new user")
		r.Recorder.Event(instance, "Error", "Failed", err.Error())
		return ctrl.Result{}, err
	}

	instance.Status.Ready = true
	err = r.Status().Update(context.Background(), instance)
	if err != nil {
		return reconcile.Result{}, err
	}

	r.Recorder.Event(instance, "Normal", "Created", "PostgreSQL user created")

	return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *PostgresUserReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&postgresv1.PostgresUser{}).
		Complete(r)
}
