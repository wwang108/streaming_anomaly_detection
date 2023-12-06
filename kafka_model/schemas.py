transaction_schema = """{
  "type": "record",
  "namespace": "com.example",
  "name": "Transaction",
  "fields": [
    {
      "name": "date",
      "type": ["null", "string"],
      "default": null
    },
    {
      "name": "hash",
      "type": ["null", "string"],
      "default": null
    },
    {
      "name": "size",
      "type": ["null", "int"],
      "default":  null
    },
    {
      "name": "virtual_size",
      "type": ["null", "int"],
      "default":  null
    },
    {
      "name": "version",
      "type": ["null", "int"],
      "default":  null
    },
    {
      "name": "lock_time",
      "type": ["null", "int"],
      "default":  null
    },
    {
      "name": "block_hash",
      "type": ["null", "string"],
      "default":  null
    },
    {
      "name": "block_number",
      "type": ["null", "int"],
      "default":  null
    },
    {
      "name": "block_timestamp",
      "type": ["null", "string"],
      "default":  null
    },
    {
      "name": "index",
      "type": ["null", "int"],
      "default":  null
    },
    {
      "name": "input_count",
      "type": ["null", "int"],
      "default":  null
    },
    {
      "name": "output_count",
      "type": ["null", "int"],
      "default":  null
    },
    {
      "name": "input_value",
      "type": ["null", "double"],
      "default":  null
    },
    {
      "name": "output_value",
      "type": ["null", "double"],
      "default":  null
    },
    {
      "name": "is_coinbase",
      "type": ["null", "boolean"],
      "default":  null
    },
    {
      "name": "fee",
      "type": ["null", "double"],
      "default":  null
    },
    {
      "name": "inputs",
      "type": ["null", {
        "type": "array",
        "items": {
          "type": "record",
          "name": "Input",
          "fields": [
            {
              "name": "index",
              "type": ["null", "int"],
              "default":  null
            },
            {
              "name": "spent_transaction_hash",
              "type": ["null", "string"],
              "default":  null
            },
            {
              "name": "spend_output_index",
              "type": ["null", "int"],
              "default":  null
            },
            {
              "name": "script_asm",
              "type": ["null", "string"],
              "default":  null
            },
            {
              "name": "script_hex",
              "type": ["null", "string"],
              "default":  null
            },
            {
              "name": "sequence",
              "type": ["null", "int"],
              "default":  null
            },
            {
              "name": "required_signatures",
              "type": ["null", "int"],
              "default":  null
            },
            {
              "name": "type",
              "type": ["null", "string"],
              "default":  null
            },
            {
              "name": "address",
              "type": ["null", "string"],
              "default":  null
            },
            {
              "name": "value",
              "type": ["null", "double"],
              "default":  null
            },
            {
              "name": "txinwitness",
              "type": ["null", {"type": "array", "items": "string"}],
              "default": null
            }
          ]
        }
      }],
      "default":  null
    },
    {
      "name": "outputs",
      "type": ["null", {
        "type": "array",
        "items": {
          "type": "record",
          "name": "Output",
          "fields": [
            {
              "name": "index",
              "type": ["null", "int"],
              "default":  null
            },
            {
              "name": "script_asm",
              "type": ["null", "string"],
              "default":  null
            },
            {
              "name": "script_hex",
              "type": ["null", "string"],
              "default":  null
            },
            {
              "name": "required_signatures",
              "type": ["null", "int"],
              "default":  null
            },
            {
              "name": "type",
              "type": ["null", "string"],
              "default":  null
            },
            {
              "name": "address",
              "type": ["null", "string"],
              "default":  null
            },
            {
              "name": "value",
              "type": ["null", "double"],
              "default":  null
            }
          ]
        }
      }],
      "default":  null
    }
  ]
}"""
