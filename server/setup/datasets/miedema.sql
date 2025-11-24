BEGIN TRANSACTION;

drop schema if exists "miedema" cascade;

create schema "miedema";
set search_path to "miedema";

CREATE TABLE customer(
    cID DECIMAL(5,0) PRIMARY KEY,
    cName VARCHAR(255) NOT NULL,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL
);

CREATE TABLE store(
    sID DECIMAL(5,0) PRIMARY KEY,
    sName VARCHAR(255) NOT NULL,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL
);

CREATE TABLE product(
    pID DECIMAL(5,0) PRIMARY KEY,
    pName VARCHAR(255) NOT NULL,
    suffix VARCHAR(255)
);

CREATE TABLE shoppinglist(
    cID DECIMAL(5,0) REFERENCES customer(cID),
    pID DECIMAL(5,0) REFERENCES product(pID),
    quantity DECIMAL(10,0) NOT NULL,
    date DATE NOT NULL,
    PRIMARY KEY(cID, pID)
);

CREATE TABLE transaction(
    tID DECIMAL(5,0),
    cID DECIMAL(5,0) NOT NULL REFERENCES customer(cID),
    sID DECIMAL(5,0) NOT NULL REFERENCES store(sID),
    pID DECIMAL(5,0) REFERENCES product(pID),
    date DATE NOT NULL,
    quantity DECIMAL(10,0) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY(tID, pID)
);

CREATE TABLE inventory(
    sID DECIMAL(5,0) REFERENCES store(sID),
    pID DECIMAL(5,0) REFERENCES product(pID),
    date DATE NOT NULL,
    quantity DECIMAL(10) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY(sID, pID, date)
);

INSERT INTO customer VALUES
(0, 'Noah', 'Koestraat', 'Ultrecht'),
(1, 'Sem', 'Rozemarijnstraat', 'Breda'),
(2, 'Lucas', 'Oude Leliestraat', 'Amsterdam'),
(3, 'Daan',  'Kalverstraat', 'Amsterdam');

INSERT INTO store VALUES
(0, 'Coop', 'Kalverstraat', 'Amsterdam'),
(1, 'Lidl', 'Hoogstraat', 'Utrecht'),
(2, 'Lidl', 'Molenstraat', 'Eindhoven'),
(3, 'Hoogvliet', 'Rozemarijnstraat', 'Breda'),
(4, 'Sligro', 'Stationsplein', 'Breda');


INSERT INTO product VALUES
(1, 'Milk', '""'),
(2, 'Mushrooms', '""'),
(3, 'Apples', '""'),
(4, 'Tea', '""'),
(5, 'Banana', '""');

INSERT INTO transaction VALUES
(0, 0, 4, 3, '2020-05-12', 5, .4),
(1, 0, 4, 1, '2020-05-13', 2, .65),
(2, 2, 0, 4, '2020-05-13', 2, 1.3),
(3, 3, 0, 1, '2020-05-15', 1, .67);

INSERT INTO shoppinglist VALUES
(1, 2, 1, '2020-05-13'),
(1, 3, 6, '2020-05-13'),
(3, 1, 2, '2020-05-15');

INSERT INTO inventory VALUES
(0, 1, '2020-05-15', 55, .55),
(0, 2, '2020-05-15', 32, 2.3),
(1, 4, '2020-05-15', 12, 1.8),
(1, 1, '2020-05-15', 46, .6);



COMMIT;