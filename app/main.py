from fastapi import FastAPI

from app.routers import (
    auth,
    product,
    category,
    attribute_value,
    attribute,
    review,
    payment_method
)

description = ""

app = FastAPI(
    description=description,
    title="E-commerce API",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(product.router)
app.include_router(category.router)
app.include_router(attribute.router)
app.include_router(attribute_value.router)
app.include_router(payment_method.router)
app.include_router(review.router)
