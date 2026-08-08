# ${managed_marker}
# Replace these placeholder addresses with the actual SGLang metrics endpoints.
- targets:
    - 127.0.0.1:39000
  labels:
    role: sglang-unified
    expected: "false"
    node: placeholder
    endpoint: placeholder_unified

- targets:
    - 127.0.0.1:39001
  labels:
    role: sglang-prefill
    expected: "false"
    node: placeholder
    endpoint: placeholder_prefill

- targets:
    - 127.0.0.1:39002
  labels:
    role: sglang-decode
    expected: "false"
    node: placeholder
    endpoint: placeholder_decode

- targets:
    - 127.0.0.1:39003
  labels:
    role: sglang-router
    expected: "false"
    node: placeholder
    endpoint: placeholder_router
