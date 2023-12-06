from pydantic import BaseModel,Field
from typing import List, Optional
from datetime import datetime

class InputModel(BaseModel):
    index: Optional[int]= Field(default=None)
    spent_transaction_hash: Optional[str]= Field(default=None)
    spend_output_index: Optional[int]= Field(default=None)
    script_asm: Optional[str]= Field(default=None)
    script_hex: Optional[str]= Field(default=None)
    sequence: Optional[int]= Field(default=None)
    required_signatures: Optional[int]= Field(default=None)
    type: Optional[str]= Field(default=None)
    address: Optional[str]= Field(default=None)
    value: Optional[float]= Field(default=None)

class OutputModel(BaseModel):
    index: Optional[int]= Field(default=None)
    script_asm: Optional[str]= Field(default=None)
    script_hex: Optional[str]= Field(default=None)
    required_signatures: Optional[int]= Field(default=None)
    type: Optional[str]= Field(default=None)
    address: Optional[str]= Field(default=None)
    value: Optional[float]= Field(default=None)

class TransactionModel(BaseModel):
    date: Optional[str]= Field(default=None)
    hash: Optional[str]= Field(default=None)
    size: Optional[int]= Field(default=None)
    virtual_size: Optional[int]= Field(default=None)
    version: Optional[int]= Field(default=None)
    lock_time: Optional[int]= Field(default=None)
    block_hash: Optional[str]= Field(default=None)
    block_number: Optional[int]= Field(default=None)
    block_timestamp: Optional[str]= Field(default=None)
    index: Optional[int]= Field(default=None)
    input_count: Optional[int]= Field(default=None)
    output_count: Optional[int]= Field(default=None)
    input_value: Optional[float]= Field(default=None)
    output_value: Optional[float]= Field(default=None)
    is_coinbase: Optional[bool]= Field(default=None)
    fee: Optional[float]= Field(default=None)
    inputs: Optional[List[InputModel]]= Field(default=None)
    outputs: Optional[List[OutputModel]]= Field(default=None)
