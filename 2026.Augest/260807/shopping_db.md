```sql
--shopping_db 데이터베이스를 생성하고 활성화(USE)하세요.
CREATE DATABASE shopping_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

SHOW DATABASES;

USE shopping_db;

GRANT ALL PRIVILEGES ON shopping_db.* TO 'analyst'@'localhost';

FLUSH PRIVILEGES;

--users 테이블 생성:

--user_id: 정수형(INT), 기본키(PRIMARY KEY), 자동 증가(AUTO_INCREMENT)

--username: 문자열(50자), 필수 입력(NOT NULL)

--email: 문자열(100자), 필수 입력(NOT NULL), 중복 불가(UNIQUE)

--created_at: 날짜시간형(DATETIME), 기본값 현재시간(DEFAULT CURRENT_TIMESTAMP)

CREATE TABLE users(
    user_id  INT AUTO_INCREMENT,
    user_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(user_id)
);

--products 테이블 생성:

--product_id: 정수형(INT), 기본키(PRIMARY KEY), 자동 증가(AUTO_INCREMENT)

--product_name: 문자열(100자), 필수 입력(NOT NULL)

--price: 정수형(INT), 필수 입력(NOT NULL), 기본값 0

--stock_quantity: 정수형(INT), 필수 입력(NOT NULL), 기본값 0

CREATE TABLE products(
    product_id INT AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL,
    price INT NOT NULL DEFAULT 0, 
    stock_quantity INT NOT NULL DEFAULT 0,
    PRIMARY KEY(product_id)
);

--users 테이블에 회원 전화번호를 저장할 phone (문자열 20자, NULL 허용) 컬럼을 추가(ALTER TABLE)하세요.
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

--1에서 생성한 users 및 products 테이블에 초기 테스트 데이터를 삽입하고, 데이터 수정 및 삭제 작업을 수행하세요.

--users 테이블에 최소 3명 이상의 회원 데이터를 INSERT 구문으로 삽입하세요.

INSERT INTO users(user_name, email, phone)
    VALUES ('김민준', 'minjun.kim@example.com', '010-3344-5378'),
        ('이서연', 'seoyeon.lee@example.com', '010-2345-679'),
        ('박준호', 'chulsoo@example.com', '010-3456-7777');


--products 테이블에 최소 4개 이상의 상품 데이터를 단일 또는 다중 INSERT문으로 삽입하세요. (예: 무선 마우스/25000원/50개, 기계식 키보드/89000원/30개, 4K 모니터/350000원/10개, USB 허브/15000원/100개)
INSERT INTO products(product_name, price, stock_quantity)
    VALUES ('BLDC 선풍기', 35000, 40),
        ('Ryzen 7 9800X3D', 720000, 20),
        ('4k 모니터', 599000, 15),
        ('RTX 5090', 3800000, 5);
--'chulsoo@test.com' 회원의 전화번호(phone)를 '010-1234-5678'로 수정(UPDATE)하세요.
UPDATE users SET phone = '010-1234-5678' WHERE phone = '010-3456-7777';


--잘못 등록된 특정 상품(예: USB 허브)을 삭제(DELETE)하세요.

DELETE FROM products WHERE product_name = 'BLDC 선풍기';


--등록된 products 및 users 테이블에서 중복 제거, 정렬, 조회 개수 제한을 수행하는 SELECT SQL 문을 작성하세요.
--products 테이블에서 중복을 제거한 고유한 상품 재고 수량(stock_quantity) 목록을 조회하세요.
SELECT DISTINCT stock_quantity FROM products;

--products 테이블의 모든 상품을 가격(price)이 비싼 순서(내림차순)로 상품 이름과 가격을 조회하세요.
SELECT product_name, price FROM products ORDER BY product_name ASC, price DESC;

--users 테이블에서 회원 번호(user_id)가 가장 큰(최근 등록된) 회원부터 순서대로 상위 2명의 회원 정보를 조회하세요.
SELECT user_id FROM users ORDER BY user_id DESC LIMIT 2;

```
