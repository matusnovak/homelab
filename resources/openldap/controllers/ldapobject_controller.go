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
	errs "errors"
	"k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/client-go/tools/record"
	"sigs.k8s.io/controller-runtime/pkg/reconcile"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	openldapv1 "github.com/matusnovak/homelab/resources/openldap/api/v1"
)

// LdapObjectReconciler reconciles a LdapObject object
type LdapObjectReconciler struct {
	client.Client
	Scheme   *runtime.Scheme
	Recorder record.EventRecorder
}

//+kubebuilder:rbac:groups=openldap.matusnovak.com,resources=ldapobjects,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=openldap.matusnovak.com,resources=ldapobjects/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=openldap.matusnovak.com,resources=ldapobjects/finalizers,verbs=update

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
// TODO(user): Modify the Reconcile function to compare the state specified by
// the LdapObject object against the actual cluster state, and then
// perform operations to make the cluster state reflect the state specified by
// the user.
//
// For more details, check Reconcile and its Result here:
// - https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.8.3/pkg/reconcile
func (r *LdapObjectReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := log.FromContext(ctx)

	instance := &openldapv1.LdapObject{}
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

	// your logic here
	l, err := GetLdapConnection(r.Client, logger, req.Namespace)
	if err != nil {
		logger.Error(err, "Failed to get LDAP connection")
		r.Recorder.Event(instance, "Error", "Failed", err.Error())
		return ctrl.Result{}, err
	}

	defer l.Close()

	return ctrl.Result{}, errs.New("todo")
}

// SetupWithManager sets up the controller with the Manager.
func (r *LdapObjectReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&openldapv1.LdapObject{}).
		Complete(r)
}
