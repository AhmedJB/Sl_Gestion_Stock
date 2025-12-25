# Product Price Evolution API

## Endpoint: `/price-evolution`

**Method**: `POST`

**Description**: 
Retrieves the historical price evolution of a specific product sold to a specific client. This allows tracking how the selling price for a customer has changed over time.

### Request Body

```json
{
  "client_id": 123,
  "product_id": 456
}
```

- `client_id`: (Integer, Required) The ID of the client.
- `product_id`: (Integer, Required) The ID of the product.

### Response

Returns a JSON array of objects, each representing a transaction (sale) of that product to the client, ordered by date.

```json
[
    {
        "order_id": "ORD-29384",
        "date": "2024-10-15T14:30:00Z",
        "quantity": 10,
        "price_sold": 150.0,
        "price_bought": 120.0
    },
    {
        "order_id": "ORD-33421",
        "date": "2024-11-20T09:15:00Z",
        "quantity": 5,
        "price_sold": 155.0,
        "price_bought": 125.0
    }
]
```

### Error Responses

- **400 Bad Request**:
    - If `client_id` or `product_id` is missing.
    - If IDs are not valid integers.
- **401 Unauthorized**:
    - If the user is not authenticated.
