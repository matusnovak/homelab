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
	"fmt"
	"strings"

	ldap "github.com/go-ldap/ldap/v3"
	"github.com/go-logr/logr"
	"k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/client-go/tools/record"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"
	"sigs.k8s.io/controller-runtime/pkg/reconcile"

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

var LdapErrorNotFound = "No Such Object"

func ldapObjectExists(logger logr.Logger, l *ldap.Conn, dn string) (bool, error) {
	dnTokens := strings.SplitN(dn, ",", 2)
	if len(dnTokens) != 2 {
		return false, errs.New("Invalid DN provided")
	}

	baseDn := dnTokens[1]
	filter := fmt.Sprintf("(%s)", dn)

	logger.Info(fmt.Sprintf("LDAP search base: %s filter: %s", baseDn, filter))

	req := ldap.NewSearchRequest(baseDn, ldap.ScopeSingleLevel, ldap.DerefAlways, 0, 0, false,
		filter, []string{"objectClass"}, []ldap.Control{ldap.NewControlPaging(25)})

	sr, err := l.Search(req)

	if err != nil {
		if strings.Contains(err.Error(), LdapErrorNotFound) {
			logger.Info(fmt.Sprintf("LDAP search for %s found 0 entries", dn))
			return false, nil
		}
		return false, err
	}

	logger.Info(fmt.Sprintf("LDAP search for %s found %d entries", dn, len(sr.Entries)))

	return true, nil
}

func ldapObjectCreate(logger logr.Logger, l *ldap.Conn, spec openldapv1.LdapObjectSpec) error {
	attrs := make(map[string][]string)

	for _, a := range spec.Values {
		if vals, ok := attrs[a.Name]; ok {
			attrs[a.Name] = append(vals, a.Value)
		} else {
			attrs[a.Name] = []string{a.Value}
		}
	}

	req := ldap.NewAddRequest(spec.Dn, []ldap.Control{ldap.NewControlPaging(25)})

	for key, vals := range attrs {
		req.Attributes = append(req.Attributes, ldap.Attribute{Type: key, Vals: vals})
	}

	err := l.Add(req)
	return err
}

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
		r.Recorder.Event(instance, "Normal", "Failed", err.Error())
		return ctrl.Result{}, err
	}

	defer l.Close()

	exists, err := ldapObjectExists(logger, l, instance.Spec.Dn)
	if err != nil {
		logger.Error(err, fmt.Sprintf("Failed to search for %s LDAP object", instance.Spec.Dn))
		r.Recorder.Event(instance, "Normal", "Failed", err.Error())
		return ctrl.Result{}, err
	}

	if exists {
		r.Recorder.Event(instance, "Normal", "Created", "LDAP object already exists")

		instance.Status.Ready = true
		err = r.Status().Update(context.Background(), instance)
		if err != nil {
			return reconcile.Result{}, err
		}

		return ctrl.Result{}, nil
	}

	logger.Info(fmt.Sprintf("Creating new LDAP object: %s", instance.Spec.Dn))

	err = ldapObjectCreate(logger, l, instance.Spec)
	if err != nil {
		logger.Error(err, fmt.Sprintf("Failed to create new LDAP object %s", instance.Spec.Dn))
		r.Recorder.Event(instance, "Normal", "Failed", err.Error())
		return ctrl.Result{}, err
	}

	instance.Status.Ready = true
	err = r.Status().Update(context.Background(), instance)
	if err != nil {
		return reconcile.Result{}, err
	}

	r.Recorder.Event(instance, "Normal", "Created", "LDAP object created")

	return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *LdapObjectReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&openldapv1.LdapObject{}).
		Complete(r)
}
