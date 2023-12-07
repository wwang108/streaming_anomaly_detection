from pydantic import BaseModel, Field
from typing import List, Optional


# Define a model for input data of a transaction
class InputModel(BaseModel):
    index: Optional[int] = Field(default=None)  # Index of the input in the transaction
    spent_transaction_hash: Optional[str] = Field(
        default=None
    )  # Hash of the spent transaction
    spend_output_index: Optional[int] = Field(
        default=None
    )  # Index of the output in the spent transaction
    script_asm: Optional[str] = Field(
        default=None
    )  # Assembly language representation of the script
    script_hex: Optional[str] = Field(
        default=None
    )  # Hexadecimal representation of the script
    sequence: Optional[int] = Field(default=None)  # Sequence number
    required_signatures: Optional[int] = Field(
        default=None
    )  # Number of required signatures
    type: Optional[str] = Field(default=None)  # Type of input
    address: Optional[str] = Field(default=None)  # Bitcoin address
    value: Optional[float] = Field(default=None)  # Value of the input in BTC
    txinwitness: Optional[List[str]] = Field(default=None)  # Transaction witness data


# Define a model for output data of a transaction
class OutputModel(BaseModel):
    index: Optional[int] = Field(default=None)
    script_asm: Optional[str] = Field(default=None)
    script_hex: Optional[str] = Field(default=None)
    required_signatures: Optional[int] = Field(default=None)
    type: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    value: Optional[float] = Field(default=None)


# Define a model for creating a transaction
class CreateTransactionCommand(BaseModel):
    date: Optional[str] = Field(default=None)  # Date of the transaction
    hash: Optional[str] = Field(default=None)  # Hash of the transaction
    size: Optional[int] = Field(default=None)  # Size of the transaction in bytes
    virtual_size: Optional[int] = Field(default=None)  # Virtual size of the transaction
    version: Optional[int] = Field(default=None)  # Version of the transaction
    lock_time: Optional[int] = Field(default=None)  # Lock time of the transaction
    block_hash: Optional[str] = Field(
        default=None
    )  # Hash of the block containing the transaction
    block_number: Optional[int] = Field(default=None)  # Block number in the blockchain
    block_timestamp: Optional[str] = Field(default=None)  # Timestamp of the block
    index: Optional[int] = Field(default=None)  # Transaction index in the block
    input_count: Optional[int] = Field(
        default=None
    )  # Number of inputs in the transaction
    output_count: Optional[int] = Field(
        default=None
    )  # Number of outputs in the transaction
    input_value: Optional[float] = Field(default=None)  # Total value of inputs in BTC
    output_value: Optional[float] = Field(default=None)  # Total value of outputs in BTC
    is_coinbase: Optional[bool] = Field(
        default=None
    )  # Flag to indicate if the transaction is a coinbase transaction
    fee: Optional[float] = Field(default=None)  # Transaction fee in BTC
    inputs: Optional[List[InputModel]] = Field(default=None)  # List of inputs
    outputs: Optional[List[OutputModel]] = Field(default=None)  # List of outputs


# Define a model for creating a prediction
class CreatePredictCommand(BaseModel):
    size: int  # Size of the transaction
    virtual_size: int  # Virtual size of the transaction
    input_count: int  # Number of inputs
    output_count: int  # Number of outputs
    input_value: float  # Total value of inputs
    output_value: float  # Total value of outputs
    fee: float  # Transaction fee
