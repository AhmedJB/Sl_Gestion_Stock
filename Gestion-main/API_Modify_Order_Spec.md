# Modify Order API Specification

## Endpoint: `/modorder`

**Method**: `POST`

**Description**: 
Modifies an existing order. This includes updating product quantities, prices, removing items, changing payment details, and **reassigning the order to a different client**.

### Usage Scenarios
1.  **Correction**: User selected the wrong product or quantity.
2.  **Client Change**: User accidentally assigned the order to "Client A" instead of "Client B".

### Request Body

```json
{
  "details": {
    "o_id": "ORD-12345678",        // (String, Required) The ID of the order to modify
    "client_id": 12,               // (Integer, Optional) ID of the NEW client. If omitted, client remains unchanged.
    "paid": 100.0,                 // (Float) The TOTAL amount paid so far (New Value)
    "mode": 1,                     // (Integer) Payment mode ID
    "transport": "Domicile",       // (String) Transport method
    "details": [                   // List of products to UPDATE
      {
        "id": 55,                  // (Integer) The ID of the OrderDetails line item
        "quantity": 5,             // (Integer) New Quantity
        "prix": 20.0               // (Float) New Unit Price (Selling Price)
      }
    ]
  },
  "ret": 0.0,                      // (Float) Amount returned (if applicable, usually 0)
  "deleted": [                     // List of products to REMOVE from order
    {
      "id": 56,                    // (Integer) OrderDetails ID to delete
      "quantity": 2                // (Integer) Quantity to return to stock
    }
  ]
}
```

### Server-Side Logic Highlights
- **Stock**: 
    - Decreasing quantity in order -> Increases Product Stock.
    - Increasing quantity in order -> Decreases Product Stock (validation checks applied).
- **Client Credit (Debt)**:
    - If `client_id` changes: The previous debt is removed from the old client, and the calculated new debt is added to the new client.
    - If `client_id` is same: The difference in debt is applied.

### Response

```json
{
  "error": false,
  "msg": "Success"  // Optional
}
```

### Error Responses
- **500 Internal Server Error**:
    - If stock becomes negative.
    - If One of the IDs is invalid.
    - `{ "error": true, "msg": "Produit Introuvable" }`
