JSON Schema to Python Classes converter. I created this since it seems
the other projects either are abandoned, or they weren’t able to parse
K8s JSON Schema definitions.

Furthermore this converter generates definitions that ``mypy`` can
consume.

Install
=======

.. code:: sh

    pip install json2pyclass

Usage
=====

.. code:: text

    Usage: json2pyclass [OPTIONS] INPUT_FILE OUTPUT_NAME

    Options:
      --mode TEXT                   Output mode [class|dict]. Dict is not yet
                                    implemented.  [default: class]

      --optionals / --no-optionals  Disable Optional[] generation.  [default:
                                    True]

      --help                        Show this message and exit.

The ``--optionals`` from the actual types can be disabled if the data
will be read, and you don’t want to always do ``if`` checks. For example
in K8s most fields are optional, even namespace names, or metadata. When
reading these values are always present, so you might want to just be
able to access them as they are, without having to ``assert`` each value
to make ``mypy`` happy.

In the future the plan is to implement also a ``Dict`` writer, that
doesn’t dump custom classes. The advantage will be that you could do
after this ``json.load_safe`` and just cast to the type.

Currently this API was created for usage with either ``addict``, or the
kubeapi part of ``adhesive``, that returns types with the properties as
regular class "fields".

Sample
======

Assuming we have a definition such as:

.. code:: json

    {
      "definitions": {
        "io.k8s.api.admissionregistration.v1.MutatingWebhook": {
          "description": "MutatingWebhook describes an admission webhook and the resources and operations it applies to.",
          "properties": {
            "admissionReviewVersions": {
              "description": "AdmissionReviewVersions is an ordered list of preferred `AdmissionReview` versions the Webhook expects. API server will try to use first version in the list which it supports. If none of the versions specified in this list supported by API server, validation will fail for this object. If a persisted webhook configuration specifies allowed versions and does not include any versions known to the API Server, calls to the webhook will fail and be subject to the failure policy.",
              "items": {
                "type": "string"
              },
              "type": "array",
    ...

We could call:

.. code:: python

    json2pyclass mydefinitions.json mydefinitions.py

And this will yield a file with all the types defined in there:

.. code:: python

    from typing import Optional, Union, List, Dict, Any

    class MutatingWebhook:  # io.k8s.api.admissionregistration.v1.MutatingWebhook
        """
        MutatingWebhook describes an admission webhook and the resources and operations it applies to.
        """
        admissionReviewVersions: List[str]
        clientConfig: 'WebhookClientConfig'
        failurePolicy: str
        matchPolicy: str
    # ...
