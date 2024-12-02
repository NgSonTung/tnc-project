
-- use master
-- drop database TNCShop

create database TNCShop
go
--ALTER DATABASE TNCShop
--    COLLATE Vietnamese_CI_AS ;
use TNCShop
go
alter database TNCShop set TRUSTWORTHY ON
go
create table Category
(
	CategoryID int identity(1,1) primary key,
	CategoryName nvarchar(30) unique not null,
	CreatedAt datetime default CURRENT_TIMESTAMP not null
)
go
create table Brand
(
	BrandID int identity(1,1) primary key,
	BrandName nvarchar(30) unique not null,
	CreatedAt datetime default CURRENT_TIMESTAMP not null

)
go
create table LS_Status
(
	StatusID int identity(1,1) primary key,
	StatusName nvarchar(100),
	TypeStatus int,--1 cua product --2 cua don hang ,
	Mark nvarchar(max),
	CreatedAt datetime default CURRENT_TIMESTAMP not null
)
go
create table Product
(
	ProductID int identity(1,1) primary key,
	Stock int not null,
	Name nvarchar (200) not null unique,
	Favorite int not null check (favorite in (1,0)),
	CategoryID int constraint FK_Product_cate references Category(categoryID) not null,
	Price float not null,
	BrandID int constraint FK_Product_brand references Brand(brandID) not null,
	Image nvarchar(max),
	Sale nvarchar(100) ,
	Description nvarchar(max),
	StatusID int constraint FK_Product_Status references LS_Status(StatusID),
	CreatedAt datetime default CURRENT_TIMESTAMP not null
)

go
create table Rating
(
	RatingID int identity(1,1) primary key,
	_5star int default 0 ,
	_4star int default 0 ,
	_3star int default 0 ,
	_2star int default 0 ,
	_1star int default 0 ,
	ProductID int constraint FK_Rating references Product(productID),
	CreatedAt datetime default CURRENT_TIMESTAMP not null
)
go
create table Auth
(
	AuthID int identity(1,1) primary key,
	AuthName nvarchar(100),
	CreatedAt datetime default CURRENT_TIMESTAMP not null
)
go
create table Users
(
	UserID int identity(1,1) primary key,
	UserName varchar(30) not null unique,
	FullName nvarchar(max),
	Password varchar(max) not null,
	AuthID int constraint FK_Users_Auth references Auth(AuthID),
	Email varchar(100) unique null ,
	Point float,
	Address nvarchar(max) null,
	Phone nvarchar(11) null,
	CreatedAt datetime default CURRENT_TIMESTAMP null
)
go

create table Subimg
(
	SubimgID int identity(1,1) primary key,
	Image varchar(max) not null,
	Alt varchar(100) not null,
	ProductID int constraint FK_SrcImg references product(productID),
	CreatedAt datetime default CURRENT_TIMESTAMP not null
)
go
create table Payment
(
	PaymentID int identity(1,1) primary key,
	PaymentName nvarchar(max),
	PaymentType nvarchar(100),
	CreatedAt datetime default CURRENT_TIMESTAMP not null
)
go
create table Orders
(
	OrderID int identity(1,1) primary key,
	UserID int constraint FK_Order_User references Users(userID),
	CustomerName nvarchar(max) null ,
	Address nvarchar(max) null,
	Phone nvarchar(11) null,
	PaymentID int constraint FK_Order_Payment references Payment(PaymentId),
	StatusID int constraint FK_Order_LS_Status references LS_Status(StatusID),
	PayIn datetime null,
	CreatedAt datetime default CURRENT_TIMESTAMP not null
)
go
create table Order_Details
(
	OrderID int ,
	ProductID int,
	Amount int,
	primary key (OrderID,ProductID),
	CreatedAt datetime default CURRENT_TIMESTAMP not null
)
go
alter table Order_Details add  constraint FK_Order_Details_Orders foreign key (OrderID)  references Orders(OrderID)
go
alter table Order_Details add  constraint FK_Order_Details_Product foreign key (ProductID)  references Product(ProductID)
go
create table Feature
(
	FeatureID int identity (1,1) primary key,
	Feature nvarchar(max) not null,
	ProductID int constraint FK_Feature_Product  references Product(productID),
	CreatedAt datetime default CURRENT_TIMESTAMP not null
)
go

create table Token
(
	ID int identity (1,1) primary key,
	UserID int constraint FK_Token_User references Users(UserID),
	RefreshToken nvarchar(max),
	Expires datetime,
	CreatedAt datetime default CURRENT_TIMESTAMP
)

go
CREATE TRIGGER tr_product_delete
ON product
INSTEAD OF DELETE
AS
BEGIN
	DELETE FROM rating WHERE productID IN (SELECT deleted.productID
	FROM deleted);
	DELETE FROM feature WHERE productID IN (SELECT deleted.productID
	FROM deleted);
	DELETE FROM Order_Details WHERE productID IN (SELECT deleted.productID
	FROM deleted);
	DELETE FROM subImg WHERE productID IN (SELECT deleted.productID
	FROM deleted);
	DELETE FROM product WHERE productID IN (SELECT deleted.productID
	FROM deleted);
END;

go

CREATE TRIGGER tr_product_create
ON product
AFTER INSERT
AS
BEGIN
	INSERT INTO Rating
		(_5star,_4star,_3star,_2star,_1star,productID)
	VALUES
		(0, 0, 0, 0, 0, (SELECT inserted.productID
			FROM inserted))
END;

go
CREATE TRIGGER tr_user_delete
ON users
INSTEAD OF DELETE
AS
BEGIN
	DELETE FROM Orders WHERE UserID IN (SELECT deleted.UserID
	FROM deleted);
	DELETE FROM users WHERE UserID IN (SELECT deleted.UserID
	FROM deleted);
END;

go

CREATE TRIGGER tr_Orders_delete
ON Orders
INSTEAD OF DELETE
AS
BEGIN
	DELETE FROM Order_Details WHERE OrderID IN (SELECT deleted.OrderID
	FROM deleted);
	DELETE FROM Orders WHERE OrderID IN (SELECT deleted.OrderID
	FROM deleted);
END;

go

CREATE FUNCTION [dbo].[fuConvertToUnsign1] ( @strInput NVARCHAR(4000) ) RETURNS NVARCHAR(4000) AS BEGIN
	IF @strInput IS NULL RETURN @strInput
	IF @strInput = '' RETURN @strInput
	DECLARE @RT NVARCHAR(4000)
	DECLARE @SIGN_CHARS NCHAR(136)
	DECLARE @UNSIGN_CHARS NCHAR (136)
	SET @SIGN_CHARS = N'ăâđêôơưàảãạáằẳẵặắầẩẫậấèẻẽẹéềểễệế ìỉĩịíòỏõọóồổỗộốờởỡợớùủũụúừửữựứỳỷỹỵý Ă ĐÊÔƠƯÀẢÃẠÁẰẲẴẶẮẦẨẪẬẤÈẺẼẸÉỀỂỄỆẾÌỈĨỊÍ ÒỎÕỌÓỒỔỖỘỐỜỞỠỢỚÙỦŨỤÚỪỬỮỰỨỲỶỸỴÝ' +NCHAR(272)+ NCHAR(208)
	SET @UNSIGN_CHARS = N'aadeoouaaaaaaaaaaaaaaaeeeeeeeeee iiiiiooooooooooooooouuuuuuuuuuyyyyy AADEOOUAAAAAAAAAAAAAAAEEEEEEEEEEIIIII OOOOOOOOOOOOOOOUUUUUUUUUUYYYYYDD'
	DECLARE @COUNTER int
	DECLARE @COUNTER1 int
	SET @COUNTER = 1
	WHILE (@COUNTER <=LEN(@strInput)) BEGIN
		SET @COUNTER1 = 1
		WHILE (@COUNTER1 <=LEN(@SIGN_CHARS)+1) BEGIN
			IF UNICODE(SUBSTRING(@SIGN_CHARS, @COUNTER1,1)) = UNICODE(SUBSTRING(@strInput,@COUNTER ,1) ) BEGIN
				IF @COUNTER=1 SET @strInput = SUBSTRING(@UNSIGN_CHARS, @COUNTER1,1) + SUBSTRING(@strInput, @COUNTER+1,LEN(@strInput)-1) ELSE SET @strInput = SUBSTRING(@strInput, 1, @COUNTER-1) +SUBSTRING(@UNSIGN_CHARS, @COUNTER1,1) + SUBSTRING(@strInput, @COUNTER+1,LEN(@strInput)- @COUNTER)
				BREAK
			END
			SET @COUNTER1 = @COUNTER1 +1
		END
		SET @COUNTER = @COUNTER +1
	END
	SET @strInput = replace(@strInput,' ','-')
	RETURN @strInput
END
go
-- select * from product where dbo.fuConvertToUnsign1(name)  like  N'%' + dbo.fuConvertToUnsign1(N'đồ') + '%'
go
select *
from Product
select *
from feature
select *
from rating
select *
from Subimg
select *
from Orders
select *
from Users
select *
from Order_Details
select *
from category
select *
from Payment
select *
from Auth
select *
from LS_Status

--DBCC CHECKIDENT ('auth', RESEED, 1)
--delete auth
use tncshop
select *
FROM Orders
where OrderID = 2

use tncshop
SELECT *
from Users
	inner join Orders on Users.UserID = Orders.UserID
	inner join (
   select Order_Details.OrderID,
		sum(Order_Details.Amount * Product.Price) as TotalPrice
	from Order_Details
		inner join Product
		on Order_Details.ProductID = Product.ProductID
	group by Order_Details.OrderID
 ) as Order_Details on Order_Details.OrderID = Orders.OrderID
where Users.UserID = 1