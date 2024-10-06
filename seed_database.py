from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import(
    User, Product, Category, Cart, Order, PaymentMethod, ShippingAddress, Review, Attribute,
    AttributeValue, DeliveryType, OrderStatus)


DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


def seed_database():
    parent_category1 = Category(title="Спортивные товары")
    parent_category2 = Category(title="Одежда")

    child_category1 = Category(title="Экипировка", parent=parent_category1)
    child_category2 = Category(title="Аксессуары", parent=parent_category1)
    child_category3 = Category(title="Игровые принадлежности", parent=parent_category1)
    child_category4 = Category(title="Спортивная одежда", parent=parent_category2)
    child_category5 = Category(title="Спортивная обувь", parent=parent_category2)

    session.add_all(
        [parent_category1, parent_category2, child_category1,
         child_category2, child_category3, child_category4, child_category5])
    session.commit()

    attributes = [
        Attribute(title="Размер", in_filter=True),
        Attribute(title="Цвет", in_filter=True),
        Attribute(title="Материал", in_filter=True),
        Attribute(title="Вес", in_filter=False),
        Attribute(title="Тип", in_filter=True),
    ]

    session.add_all(attributes)
    session.commit()

    attribute_values = [
        AttributeValue(attribute_id=attributes[0].id, value="S"),
        AttributeValue(attribute_id=attributes[0].id, value="M"),
        AttributeValue(attribute_id=attributes[0].id, value="L"),
        AttributeValue(attribute_id=attributes[0].id, value="XL"),
        AttributeValue(attribute_id=attributes[1].id, value="Красный"),
        AttributeValue(attribute_id=attributes[1].id, value="Синий"),
        AttributeValue(attribute_id=attributes[1].id, value="Черный"),
        AttributeValue(attribute_id=attributes[1].id, value="Белый"),
        AttributeValue(attribute_id=attributes[2].id, value="Хлопок"),
        AttributeValue(attribute_id=attributes[2].id, value="Полиэстер"),
        AttributeValue(attribute_id=attributes[2].id, value="Нейлон"),
        AttributeValue(attribute_id=attributes[3].id, value="300 г"),
        AttributeValue(attribute_id=attributes[4].id, value="Теннис"),
        AttributeValue(attribute_id=attributes[4].id, value="Футбол"),
        AttributeValue(attribute_id=attributes[4].id, value="Баскетбол"),
    ]

    session.add_all(attribute_values)
    session.commit()

    products = [
        Product(
            title="Футболка Adidas",
            description="Удобная футболка для тренировок",
            price=2500.0,
            discount=5.0,
            quantity=100,
            category_id=child_category4.id,
            attributes=[attribute_values[0], attribute_values[4]]
        ),
        Product(
            title="Футболка Adidas",
            description="Удобная футболка для тренировок",
            price=2500.0,
            discount=5.0,
            quantity=100,
            category_id=child_category4.id,
            attributes=[attribute_values[1], attribute_values[4]]
        ),
        Product(
            title="Футболка Adidas",
            description="Удобная футболка для тренировок",
            price=2500.0,
            discount=5.0,
            quantity=100,
            category_id=child_category4.id,
            attributes=[attribute_values[2], attribute_values[4]]
        ),
        Product(
            title="Кроссовки Nike",
            description="Легкие и удобные кроссовки для бега",
            price=7500.0,
            discount=None,
            quantity=50,
            category_id=child_category5.id
        ),
        Product(
            title="Спортивные штаны Puma",
            description="Комфортные штаны для спорта и отдыха",
            price=4500.0,
            discount=10.0,
            quantity=80,
            category_id=child_category4.id
        ),
        Product(
            title="Водонепроницаемая куртка The North Face",
            description="Куртка для активного отдыха в дождливую погоду",
            price=12000.0,
            discount=15.0,
            quantity=30,
            category_id=child_category4.id
        ),
        Product(
            title="Рюкзак Osprey",
            description="Удобный рюкзак для походов",
            price=8500.0,
            discount=5.0,
            quantity=60,
            category_id=child_category2.id
        ),
        Product(
            title="Бутсы Adidas",
            description="Профессиональные бутсы для футбольных матчей",
            price=9000.0,
            discount=20.0,
            quantity=40,
            category_id=child_category5.id
        ),
        Product(
            title="Теннисная ракетка Wilson",
            description="Легкая и мощная ракетка для тенниса",
            price=11000.0,
            discount=None,
            quantity=20,
            category_id=child_category3.id,
            attributes=[attribute_values[-3]]
        ),
        Product(
            title="Набор гантелей",
            description="Комплект гантелей для домашних тренировок",
            price=5000.0,
            discount=None,
            quantity=15,
            category_id=child_category1.id
        ),
        Product(
            title="Фляга для воды",
            description="Легкая фляга для походов и тренировок",
            price=1500.0,
            discount=None,
            quantity=100,
            category_id=child_category1.id
        ),
        Product(
            title="Спортивная бутылка с фильтром",
            description="Бутылка с встроенным фильтром для чистой воды",
            price=3000.0,
            discount=None,
            quantity=50,
            category_id=child_category1.id
        ),
    ]

    session.add_all(products)
    session.commit()

    print("База данных успешно заполнена!")


if __name__ == "__main__":
    seed_database()
    session.close()
