import datetime
from typing import List, Union, Dict
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine("sqlite:///restaurant.db")
Base = declarative_base()


class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True)
    size = Column(Integer)
    is_available = Column(String, default="Yes")
    reservations = relationship("Reservation", back_populates="table")
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"{self.id} - Size: {self.size} | Available: {self.is_available} | Created: {self.created_date}"


class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True)
    customer_name = Column(String)
    party_size = Column(Integer)
    reservation_time = Column(DateTime)
    table_id = Column(Integer, ForeignKey("tables.id"))
    table = relationship("Table", back_populates="reservations")
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"{self.id} - Customer: {self.customer_name} | Party Size: {self.party_size} | Table ID: {self.table_id} | Reservation Time: {self.reservation_time} | Created: {self.created_date}"


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


class Restaurant:
    def __init__(
        self,
        name: str,
        address: str,
        phone_number: str,
        menu: List[Dict[str, Union[str, float]]],
    ) -> None:
        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.menu = menu

    def add_table(self, table_size: int) -> None:
        new_table = Table(size=table_size)
        session.add(new_table)
        session.commit()

    def list_tables(self) -> None:
        tables = session.query(Table).all()
        for table in tables:
            print(table)

    def reserve_table(
        self, customer_name: str, party_size: int, reservation_time: datetime.datetime
    ) -> None:
        available_tables = session.query(Table).filter_by(is_available="Yes").all()

        if not available_tables:
            print("No available tables for the specified reservation time.")
            return

        selected_table = available_tables[0]
        reservation = Reservation(
            customer_name=customer_name,
            party_size=party_size,
            reservation_time=reservation_time,
            table_id=selected_table.id,
        )

        selected_table.is_available = "No"
        session.add(reservation)
        session.commit()
        print(f"Table {selected_table.id} reserved successfully for {customer_name}.")

    def list_reservations(self) -> None:
        reservations = session.query(Reservation).all()
        for reservation in reservations:
            print(reservation)

    def cancel_reservation(self, reservation_id: int) -> None:
        reservation = session.query(Reservation).get(reservation_id)

        if reservation:
            table = session.query(Table).get(reservation.table_id)
            table.is_available = "Yes"
            session.delete(reservation)
            session.commit()
            print(f"Reservation {reservation_id} canceled successfully.")
        else:
            print(f"Reservation {reservation_id} not found.")


restaurant = Restaurant(
    "End of The World", "Sauletekio al., Vilnius", "+370*******", []
)

while True:
    option = int(
        input(
            "Choose option: \n1 - List Tables \n2 - Add Table \n3 - List Reservations \n4 - Cancel Reservation \n5 - Reserve table \n6 - Exit\n"
        )
    )

    if option == 1:
        restaurant.list_tables()

    elif option == 2:
        table_size = int(input("Enter the size of the table: "))
        restaurant.add_table(table_size)

    elif option == 3:
        restaurant.list_reservations()

    elif option == 4:
        reservation_id = int(input("Enter the reservation ID to cancel: "))
        restaurant.cancel_reservation(reservation_id)

    elif option == 5:
        customer_name = input("Please provide your name: ")
        party_size = int(input("How many people will be there? "))
        time_format = "%Y-%m-%d %H"
        reservation_time_str = input("Enter reservation time (YYYY-MM-DD HH): ")

        try:
            reservation_time = datetime.datetime.strptime(
                reservation_time_str, time_format
            )
        except ValueError:
            print("Invalid date format. Please use the format specified.")
            continue

        restaurant.reserve_table(customer_name, party_size, reservation_time)

    elif option == 6:
        break
