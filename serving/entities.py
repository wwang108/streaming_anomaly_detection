from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Model for individual transaction input data
class InputModel(BaseModel):
    index: Optional[int] = Field(default=None)  # Index of this input in the transaction
    spent_transaction_hash: Optional[str] = Field(default=None)
    spend_output_index: Optional[int] = Field(default=None)
    script_asm: Optional[str] = Field(default=None)
    script_hex: Optional[str] = Field(default=None)
    sequence: Optional[int] = Field(default=None)
    required_signatures: Optional[int] = Field(default=None)
    type: Optional[str] = Field(default=None)  # Input type
    address: Optional[str] = Field(default=None)  # Associated Bitcoin address
    value: Optional[float] = Field(default=None)  # Value of the input in BTC
    txinwitness: Optional[List[str]] = Field(default=None)  # Transaction witness data


# Model for individual transaction output data
class OutputModel(BaseModel):
    index: Optional[int] = Field(default=None)
    script_asm: Optional[str] = Field(default=None)
    script_hex: Optional[str] = Field(default=None)
    required_signatures: Optional[int] = Field(default=None)
    type: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    value: Optional[float] = Field(default=None)


# Model for a complete Bitcoin transaction
class TransactionModel(BaseModel):
    date: Optional[str] = Field(default=None)  # Transaction date
    hash: Optional[str] = Field(default=None)  # Transaction hash
    size: Optional[int] = Field(default=None)
    virtual_size: Optional[int] = Field(default=None)  # Transaction virtual size
    version: Optional[int] = Field(default=None)  # Transaction version
    lock_time: Optional[int] = Field(default=None)  # Transaction lock time
    block_hash: Optional[str] = Field(default=None)
    block_number: Optional[int] = Field(default=None)
    block_timestamp: Optional[str] = Field(default=None)  # Timestamp of the block
    index: Optional[int] = Field(default=None)
    input_count: Optional[int] = Field(
        default=None
    )  # Number of inputs in the transaction
    output_count: Optional[int] = Field(
        default=None
    )  # Number of outputs in the transaction
    input_value: Optional[float] = Field(
        default=None
    )  # Total value of all inputs in BTC
    output_value: Optional[float] = Field(
        default=None
    )  # Total value of all outputs in BTC
    is_coinbase: Optional[bool] = Field(
        default=None
    )  # Flag indicating if this is a coinbase transaction
    fee: Optional[float] = Field(default=None)  # Transaction fee in BTC
    inputs: Optional[List[InputModel]] = Field(default=None)  # List of input models
    outputs: Optional[List[OutputModel]] = Field(default=None)  # List of output models
