# Functions

Functions are the heart of TinyBase's extensibility. They let you define server-side logic with full type safety, automatic API exposure, and execution tracking.

## Overview

A TinyBase function is:

- A **Python callable** decorated with `@register`
- **Typed** with Pydantic input/output models
- **Exposed** as an HTTP endpoint at `/api/functions/{name}`
- **Tracked** with execution metadata (status, duration, errors)
- **Schedulable** for automated execution

## Defining Functions

Functions are defined in individual files within the `functions/` package directory. Each function should live in its own file, allowing you to use uv's single-file script feature for inline dependencies.

### Basic Structure

```python title="functions/my_function.py"
from pydantic import BaseModel
from tinybase.functions import Context, register


class MyInput(BaseModel):
    """Input model - define expected parameters."""
    param1: str
    param2: int = 0  # Optional with default


class MyOutput(BaseModel):
    """Output model - define response structure."""
    result: str
    success: bool


@register(
    name="my_function",           # Unique name (used in URLs)
    description="What it does",    # For documentation
    auth="auth",                   # Access level
    input_model=MyInput,           # Input validation
    output_model=MyOutput,         # Output schema
    tags=["category"],             # For grouping
)
def my_function(ctx: Context, payload: MyInput) -> MyOutput:
    """Implementation goes here."""
    return MyOutput(result=f"Got {payload.param1}", success=True)
```

### The @register Decorator

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique function identifier |
| `description` | `str` | Human-readable description |
| `auth` | `str` | Access level: `"public"`, `"auth"`, `"admin"` |
| `input_model` | `type[BaseModel]` | Pydantic model for input |
| `output_model` | `type[BaseModel]` | Pydantic model for output |
| `tags` | `list[str]` | Categorization tags |

### Authentication Levels

| Level | Description |
|-------|-------------|
| `public` | No authentication required |
| `auth` | Any authenticated user |
| `admin` | Admin users only |

## The Context Object

Every function receives a `Context` object with execution information:

```python
@dataclass
class Context:
    # Execution metadata
    function_name: str              # Name of this function
    trigger_type: str               # "manual" or "schedule"
    trigger_id: UUID | None         # Schedule ID if scheduled
    request_id: UUID                # Unique execution ID
    
    # User information
    user_id: UUID | None            # Current user (None for public/scheduled)
    is_admin: bool                  # Admin status
    
    # Utilities
    now: datetime                   # Current UTC time
    db: Session                     # Database session
    request: Request | None         # FastAPI request (manual triggers only)
```

### Using Context

```python
@register(name="context_demo", auth="auth", ...)
def context_demo(ctx: Context, payload: Input) -> Output:
    # Access user info
    if ctx.user_id:
        print(f"Called by user: {ctx.user_id}")
    
    # Check admin status
    if ctx.is_admin:
        # Do admin-only things
        pass
    
    # Database operations
    users = ctx.db.exec(select(User)).all()
    
    # Check trigger type
    if ctx.trigger_type == "schedule":
        print(f"Running scheduled task: {ctx.trigger_id}")
    
    # Get current time
    print(f"Execution time: {ctx.now}")
    
    return Output(...)
```

## Input and Output Models

Use Pydantic models for type-safe inputs and outputs:

### Complex Input Models

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class OrderInput(BaseModel):
    """Create a new order."""
    product_id: str = Field(..., description="Product UUID")
    quantity: int = Field(ge=1, le=100, description="Quantity (1-100)")
    notes: Optional[str] = Field(None, max_length=500)
    
    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v


class OrderOutput(BaseModel):
    """Order creation result."""
    order_id: str
    total_price: float
    estimated_delivery: datetime
```

### Nested Models

```python
class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str


class ShippingInput(BaseModel):
    order_id: str
    shipping_address: Address
    billing_address: Optional[Address] = None


class ShippingOutput(BaseModel):
    tracking_number: str
    carrier: str
```

## Calling Functions

### Via REST API

```bash
curl -X POST http://localhost:8000/api/functions/my_function \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"param1": "hello", "param2": 42}'
```

Response:

```json
{
  "call_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "succeeded",
  "result": {
    "result": "Got hello",
    "success": true
  }
}
```

### Response Structure

| Field | Description |
|-------|-------------|
| `call_id` | Unique execution ID |
| `status` | `"succeeded"` or `"failed"` |
| `result` | Output data (on success) |
| `error` | Error message (on failure) |
| `error_type` | Exception type (on failure) |

### Error Responses

```json
{
  "call_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "error": "Product not found",
  "error_type": "ValueError"
}
```

## Database Operations

Access the database through `ctx.db`:

```python
from sqlmodel import select
from tinybase.db.models import User, Record, Collection


@register(name="user_stats", auth="admin", ...)
def user_stats(ctx: Context, payload: Input) -> Output:
    # Query users
    users = ctx.db.exec(select(User)).all()
    admin_count = sum(1 for u in users if u.is_admin)
    
    # Query records
    records = ctx.db.exec(select(Record)).all()
    
    # Use the CollectionService for collections
    from tinybase.collections.service import CollectionService
    service = CollectionService(ctx.db)
    collections = service.list_collections()
    
    return Output(
        total_users=len(users),
        admin_users=admin_count,
        total_records=len(records),
        collections=len(collections)
    )
```

### Creating Records

```python
@register(name="create_item", auth="auth", ...)
def create_item(ctx: Context, payload: CreateInput) -> CreateOutput:
    from tinybase.collections.service import CollectionService
    
    service = CollectionService(ctx.db)
    collection = service.get_collection_by_name("items")
    
    record = service.create_record(
        collection,
        data={"title": payload.title, "value": payload.value},
        owner_id=ctx.user_id
    )
    
    return CreateOutput(id=str(record.id))
```

## Error Handling

Raise exceptions to report errors:

```python
@register(name="divide", auth="public", ...)
def divide(ctx: Context, payload: DivideInput) -> DivideOutput:
    if payload.divisor == 0:
        raise ValueError("Cannot divide by zero")
    
    return DivideOutput(result=payload.dividend / payload.divisor)
```

### Custom Exceptions

```python
class InsufficientFundsError(Exception):
    """Raised when account balance is too low."""
    pass


@register(name="withdraw", auth="auth", ...)
def withdraw(ctx: Context, payload: WithdrawInput) -> WithdrawOutput:
    balance = get_balance(ctx.user_id)
    
    if payload.amount > balance:
        raise InsufficientFundsError(
            f"Balance ({balance}) is less than withdrawal ({payload.amount})"
        )
    
    # Process withdrawal...
```

## Function Call Tracking

Every function execution creates a `FunctionCall` record:

```python
@dataclass
class FunctionCall:
    id: UUID                    # Unique call ID
    function_name: str          # Function name
    user_id: UUID | None        # Who called it
    trigger_type: str           # "manual" or "schedule"
    trigger_id: UUID | None     # Schedule ID
    status: str                 # "succeeded" or "failed"
    duration_ms: int            # Execution time
    error_message: str | None   # Error details
    error_type: str | None      # Exception type
    created_at: datetime        # When it ran
```

View function calls in the Admin UI under **Function Calls**.

## Generating Function Boilerplate

Use the CLI to create new functions:

```bash
tinybase functions new calculate_tax -d "Calculate tax for an order"
```

This creates a new file `functions/calculate_tax.py`:

```python title="functions/calculate_tax.py"
from pydantic import BaseModel
from tinybase.functions import Context, register


class CalculateTaxInput(BaseModel):
    """Input model for calculate_tax function."""
    # TODO: Define input fields
    pass


class CalculateTaxOutput(BaseModel):
    """Output model for calculate_tax function."""
    # TODO: Define output fields
    pass


@register(
    name="calculate_tax",
    description="Calculate tax for an order",
    auth="auth",
    input_model=CalculateTaxInput,
    output_model=CalculateTaxOutput,
    tags=[],
)
def calculate_tax(ctx: Context, payload: CalculateTaxInput) -> CalculateTaxOutput:
    """
    Calculate tax for an order
    
    TODO: Implement function logic
    """
    return CalculateTaxOutput()
```

## Organizing Functions

All user-defined functions must live in the `functions/` package directory. Each function should be in its own file:

```
my-app/
├── functions/
│   ├── __init__.py        # Package marker (auto-generated)
│   ├── add_numbers.py     # One function per file
│   ├── hello.py
│   ├── orders.py          # Order-related functions
│   ├── users.py           # User-related functions
│   └── reports.py         # Reporting functions
└── tinybase.toml
```

Each file can define functions independently:

```python title="functions/orders.py"
from pydantic import BaseModel
from tinybase.functions import Context, register


class CreateOrderInput(BaseModel):
    ...


@register(name="create_order", ...)
def create_order(ctx: Context, payload: CreateOrderInput) -> ...:
    ...
```

### Using uv's Single-File Script Feature

Each function file can use uv's single-file script feature to define inline dependencies. This allows you to use third-party libraries without manually managing dependencies:

```python title="functions/send_email.py"
# /// script
# dependencies = [
#   "requests>=2.31.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

from pydantic import BaseModel
from tinybase.functions import Context, register
import requests


class SendEmailInput(BaseModel):
    to: str
    subject: str
    body: str


class SendEmailOutput(BaseModel):
    success: bool
    message_id: str | None = None


@register(
    name="send_email",
    description="Send an email using an external service",
    auth="auth",
    input_model=SendEmailInput,
    output_model=SendEmailOutput,
    tags=["communication"],
)
def send_email(ctx: Context, payload: SendEmailInput) -> SendEmailOutput:
    """Send email using requests library."""
    response = requests.post(
        "https://api.example.com/send",
        json={"to": payload.to, "subject": payload.subject, "body": payload.body}
    )
    return SendEmailOutput(
        success=response.status_code == 200,
        message_id=response.json().get("id") if response.ok else None,
    )
```

When TinyBase loads this function, it will automatically detect and install the dependencies using `uv pip install`. This makes it easy to use third-party libraries without managing a global dependency list.

## Best Practices

### 1. Keep Functions Focused

Each function should do one thing well:

```python
# Good: Focused function
@register(name="send_welcome_email", ...)
def send_welcome_email(ctx: Context, payload: Input) -> Output:
    ...

# Bad: Function doing too much
@register(name="register_user_and_send_email_and_create_profile", ...)
def register_user_and_send_email_and_create_profile(...):
    ...
```

### 2. Use Descriptive Names

```python
# Good
@register(name="calculate_order_total", ...)
@register(name="send_password_reset", ...)

# Bad
@register(name="calc", ...)
@register(name="do_stuff", ...)
```

### 3. Document Your Functions

```python
@register(name="process_refund", ...)
def process_refund(ctx: Context, payload: RefundInput) -> RefundOutput:
    """
    Process a refund for an order.
    
    This function:
    1. Validates the order exists and is eligible
    2. Calculates the refund amount
    3. Updates the order status
    4. Triggers payment processor refund
    
    Raises:
        ValueError: If order not found or not eligible
        PaymentError: If refund processing fails
    """
    ...
```

### 4. Handle Errors Gracefully

```python
@register(name="external_api_call", ...)
def external_api_call(ctx: Context, payload: Input) -> Output:
    try:
        response = call_external_api(payload.data)
        return Output(result=response)
    except ConnectionError:
        raise RuntimeError("External API unavailable, please try again")
    except TimeoutError:
        raise RuntimeError("Request timed out, please try again")
```

## See Also

- [Scheduling Guide](scheduling.md) - Run functions automatically
- [Extensions Guide](extensions.md) - Hook into function lifecycle
- [Python API Reference](../reference/python-api.md) - Full API documentation

