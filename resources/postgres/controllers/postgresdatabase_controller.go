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

	"k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"
	"sigs.k8s.io/controller-runtime/pkg/reconcile"

	postgresv1 "github.com/matusnovak/homelab/resources/postgres/api/v1"
)

// PostgresDatabaseReconciler reconciles a PostgresDatabase object
type PostgresDatabaseReconciler struct {
	client.Client
	Scheme   *runtime.Scheme
	Recorder record.EventRecorder
}

//+kubebuilder:rbac:groups=postgres.matusnovak.com,resources=postgresdatabases,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=postgres.matusnovak.com,resources=postgresdatabases/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=postgres.matusnovak.com,resources=postgresdatabases/finalizers,verbs=update

func pgDatabaseExists(db *sql.DB, name string) (bool, error) {
	rows, err := db.Query("SELECT rolname FROM pg_catalog.pg_database")
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

func pgDatabaseCreate(db *sql.DB, name string, role string) error {
	_, err := db.Exec(fmt.Sprintf("CREATE DATABASE %s", name))
	if err != nil {
		return err
	}

	_, err = db.Exec(fmt.Sprintf("GRANT ALL PRIVILEGES ON DATABASE %s TO %s", name, role))
	if err != nil {
		return err
	}

	return nil
}

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
// TODO(user): Modify the Reconcile function to compare the state specified by
// the PostgresDatabase object against the actual cluster state, and then
// perform operations to make the cluster state reflect the state specified by
// the user.
//
// For more details, check Reconcile and its Result here:
// - https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.8.3/pkg/reconcile
func (r *PostgresDatabaseReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := log.FromContext(ctx)

	instance := &postgresv1.PostgresDatabase{}
	err := r.Get(context.TODO(), req.NamespacedName, instance)
	if err != nil {
		if errors.IsNotFound(err) {
			logger.Error(err, "Failed to get PostgresDatabase instance")
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
		r.Recorder.Event(instance, "Normal", "Failed", err.Error())
		return ctrl.Result{}, err
	}
	defer db.Close()

	logger.Info(fmt.Sprintf("Checking for PostgreSQL database: %s", instance.Spec.Name))

	exists, err := pgDatabaseExists(db, instance.Spec.Name)
	if err != nil {
		logger.Error(err, "Failed to check if database exists")
		r.Recorder.Event(instance, "Error", "Failed", err.Error())
		return ctrl.Result{}, err
	}

	if exists {
		r.Recorder.Event(instance, "Normal", "Created", "PostgreSQL database already exists")

		instance.Status.Ready = true
		err = r.Status().Update(context.Background(), instance)
		if err != nil {
			return reconcile.Result{}, err
		}

		return ctrl.Result{}, nil
	}

	logger.Info(fmt.Sprintf("Creating new PostgreSQL database: %s", instance.Spec.Name))

	err = pgDatabaseCreate(db, instance.Spec.Name, instance.Spec.Role)
	if err != nil {
		logger.Error(err, "Failed to create new database")
		r.Recorder.Event(instance, "Normal", "Failed", err.Error())
		return ctrl.Result{}, err
	}

	instance.Status.Ready = true
	err = r.Status().Update(context.Background(), instance)
	if err != nil {
		return reconcile.Result{}, err
	}

	r.Recorder.Event(instance, "Normal", "Created", "PostgreSQL database created")

	return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *PostgresDatabaseReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&postgresv1.PostgresDatabase{}).
		Complete(r)
}
