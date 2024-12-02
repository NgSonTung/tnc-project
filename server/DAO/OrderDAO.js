const dbConfig = require("../database/dbconfig");

const dbUtils = require("../utils/dbUtils");
const DateTimeUtils = require("../utils/DateTimeUtils");
const authUtils = require("../utils/authUtils");

const UserSchema = require("../Model/User");
const {OrdersSchema, Order_DetailsSchema} = require("../Model/Order");
const StatusSchema = require("../Model/Status");
const PaymentSchema = require("../Model/Payment");
const ProductSchema = require("../Model/Product");
const RefreshTokenSchema = require("../Model/RefreshToken");
const DTOProduct = require("../DTO/Default/DTOProduct");
const DTOProductCustomize = require("../DTO/Customize/DTOProductCustomize");
const DTOOrderDetails = require("../DTO/Default/DTOOrderDetails");
const DTOOrderCustomize = require("../DTO/Customize/DTOOrderCustomize");
const DTOOrderDetailsProductCustomize = require("../DTO/Customize/DTOOrderDetailsCustomize");

const ProductDAO = require("../DAO/ProductDAO");

exports.addOrder = async (order) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }
  const ms = DateTimeUtils.convertDateTimeToMilliseconds(Date.now());
  order.CreatedAt = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);
  if (order.PaymentID != 0) {
    order.PayIn = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);
  }
  let insertData = OrdersSchema.validateData(order);
  let query = `SET IDENTITY_INSERT ${OrdersSchema.schemaName} ON insert into ${OrdersSchema.schemaName}`;
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(OrdersSchema.schema, dbPool.request(), insertData);
  if (!insertFieldNamesStr || !insertValuesStr) {
    throw new Error("Invalid insert param");
  }

  query +=
    " (" +
    insertFieldNamesStr +
    ") select  " +
    insertValuesStr +
    ` SET IDENTITY_INSERT ${OrdersSchema.schemaName} OFF`;
  result = await request.query(query);
  return result.recordsets;
};

exports.createNewOrder = async (userID) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }
  let order = {};
  if (userID != null) {
    order.UserID = userID;
  }
  const ms = DateTimeUtils.convertDateTimeToMilliseconds(Date.now());
  const now = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);
  order.CreatedAt = now;
  let insertData = OrdersSchema.validateData(order);
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(OrdersSchema.schema, dbPool.request(), insertData);
  if (!insertFieldNamesStr || !insertValuesStr) {
    throw new Error("Invalid insert param");
  }
  const query = `insert into ${OrdersSchema.schemaName} ( ${insertFieldNamesStr} ) select ${insertValuesStr}
    select OrderID from ${OrdersSchema.schemaName} where CreatedAt = @CreatedAt
  `;
  console.log(query);
  let result = await request.query(query);
  // console.log(result);
  return result.recordset[0].OrderID;
};

exports.addOrder_DetailsIfNotExisted = async (order_details) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }
  let insertData = Order_DetailsSchema.validateData(order_details);
  let query = `insert into ${Order_DetailsSchema.schemaName}`;
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(
      Order_DetailsSchema.schema,
      dbPool.request(),
      insertData
    );
  if (!insertFieldNamesStr || !insertValuesStr) {
    throw new Error("Invalid insert param");
  }

  query +=
    " (" +
    insertFieldNamesStr +
    ") SELECT  " +
    insertValuesStr +
    ` WHERE NOT EXISTS(SELECT * FROM ${Order_DetailsSchema.schemaName} WHERE OrderID = @orderID and productID = @productID)` +
    `
    select * from ${Order_DetailsSchema.schemaName} WHERE OrderID = @orderID
    `;

  let result = await request.query(query);
  var dtos = result.recordsets[0].map((x) => new DTOOrderDetails(x));
  return dtos;
};

exports.getProductInOderByUserID = async (userID) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }

  // console.log(query);
  let result = await dbPool
    .request()
    .input(
      OrdersSchema.schema.UserID.name,
      OrdersSchema.schema.UserID.sqlType,
      userID
    ).query(` select  p.*,od.Amount from Order_Details od
       inner join Product p on p.ProductID = od.ProductID
       inner join orders o on o.OrderID = od.OrderID
       inner join LS_Status s on s.StatusID = o.StatusID
       where od.OrderID in (select OrderID from Orders o where o.UserID = @UserID ) and o.StatusID =1 and s.TypeStatus =2
      `);
  let count = await dbPool
    .request()
    .input(
      OrdersSchema.schema.UserID.name,
      OrdersSchema.schema.UserID.sqlType,
      userID
    ).query(`select  sum(amount) as TotalAmount from Order_Details od
     inner join orders o on o.OrderID = od.OrderID
     inner join LS_Status s on s.StatusID = o.StatusID
    where od.OrderID in (select OrderID from Orders o where o.UserID = @UserID ) and o.StatusID =1 and s.TypeStatus =2
  `);
  let queryoOrderID = await dbPool
    .request()
    .input(
      OrdersSchema.schema.UserID.name,
      OrdersSchema.schema.UserID.sqlType,
      userID
    )
    .query(
      `select OrderID,StatusID from Orders where UserID = @UserID and StatusID = 1`
    );
  var dtos = result.recordsets[0].map(
    (element) => new DTOOrderDetailsProductCustomize(element)
  );
  return {
    DataInOrder: dtos,
    TotalAmount: count.recordsets[0][0].TotalAmount,
    OrderID: queryoOrderID.recordsets[0][0].OrderID,
    StatusID: queryoOrderID.recordsets[0][0].StatusID,
  };
};

exports.getOrderIDByUserName = async (username) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }

  let result = await dbPool
    .request()
    .input(
      UserSchema.schema.UserName.name,
      UserSchema.schema.UserName.sqlType,
      username
    )
    .query(
      `select OrderID from ${OrdersSchema.schemaName} where UserID in (select UserID from ${UserSchema.schemaName} where userName = @${UserSchema.schema.UserName.name}) `
    );
  return result.recordsets[0];
};

exports.updateOrder_Details = async (Order_Details) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }
  let updateData = Order_DetailsSchema.validateData(Order_Details);
  let q = `update ${Order_DetailsSchema.schemaName} set `;
  // console.log(updateData);

  const {request, updateStr} = dbUtils.getUpdateQuery(
    Order_DetailsSchema.schema,
    dbPool.request(),
    updateData
  );
  if (updateData.Amount == 0) {
    q = `delete ${Order_DetailsSchema.schemaName} where ProductID =@ProductID and OrderID = @OrderID`;
  } else {
    q += updateStr + ` where ProductID =@ProductID and OrderID = @OrderID`;
  }

  const queryCombie =
    q +
    ` select * from ${Order_DetailsSchema.schemaName} where ProductID =@ProductID and OrderID = @OrderID`;
  let result = await request.query(queryCombie);
  var dto = new DTOOrderDetails(result.recordsets[0][0]);
  return dto;
};

exports.deleteItemInOrder = async (urlQuery, user) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }

  const resultQueryOrder = await dbPool
    .request()
    .input(
      OrdersSchema.schema.OrderID.name,
      OrdersSchema.schema.OrderID.sqlType,
      urlQuery.OrderID
    )
    .query(`select * from ${OrdersSchema.schemaName} where OrderID = @OrderID`);
  const order = resultQueryOrder.recordset[0];
  if (order == null) {
    throw new Error("Order not found");
  }
  if (order.PayIn != null) {
    throw new Error("Order has been paid");
  }

  //authen user
  if (user.UserID != order.UserID) {
    throw new Error("You dont have permission to delete this order");
  }

  let q = `delete Order_Details where ProductID = ${urlQuery.ProductID} and OrderID = ${urlQuery.OrderID} `;
  let result = await dbPool.request().query(q);
};

exports.getOrderByUserID = async (userID) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }
  const query = `select  ${OrdersSchema.schemaName}.*,
  ${StatusSchema.schemaName}.${StatusSchema.schema.StatusName.name},
  ${PaymentSchema.schemaName}.${PaymentSchema.schema.PaymentName.name},
  Order_Details.TotalPrice,
  Order_Details.TotalAmount
   from ${OrdersSchema.schemaName}
  inner join ${StatusSchema.schemaName} on ${OrdersSchema.schemaName}.StatusID = ${StatusSchema.schemaName}.StatusID
  inner join ${PaymentSchema.schemaName} on ${OrdersSchema.schemaName}.PaymentID = ${PaymentSchema.schemaName}.PaymentID
  inner join
  (
    select ${Order_DetailsSchema.schemaName}.OrderID,
    sum(${Order_DetailsSchema.schemaName}.Amount * ${ProductSchema.schemaName}.Price) as TotalPrice,
    count(${Order_DetailsSchema.schemaName}.Amount) as TotalAmount
    from ${Order_DetailsSchema.schemaName}
    inner join ${ProductSchema.schemaName}
    on ${Order_DetailsSchema.schemaName}.ProductID = ${ProductSchema.schemaName}.ProductID
    group by ${Order_DetailsSchema.schemaName}.OrderID
  ) as Order_Details
  on ${OrdersSchema.schemaName}.OrderID = ${Order_DetailsSchema.schemaName}.OrderID
  where UserID = @${OrdersSchema.schema.UserID.name}
  `;
  console.log(query);
  let result = await dbPool
    .request()
    .input(
      OrdersSchema.schema.UserID.name,
      OrdersSchema.schema.UserID.sqlType,
      userID
    )
    .query(query);
  let resultTotalOrder = await dbPool
    .request()
    .input(
      OrdersSchema.schema.UserID.name,
      OrdersSchema.schema.UserID.sqlType,
      userID
    ).query(`
      select count(*) as TotalOrder from ${OrdersSchema.schemaName} where UserID = @${OrdersSchema.schema.UserID.name}

    `);
  const dataArr = result.recordsets[0].map((x) => {
    x.CreatedAt = DateTimeUtils.convertSqlDateTimeToUIDateTime(x.CreatedAt);
    return new DTOOrderCustomize(x);
  });
  return {
    Data: dataArr,
    TotalOrder: resultTotalOrder.recordsets[0][0].TotalOrder,
  };
};

exports.getOrderDetailsByOrderIDUserID = async (reqHeader) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }
  const {orderid, userid} = reqHeader;
  const query = `select  ${Order_DetailsSchema.schemaName}.OrderID,
  ${ProductSchema.schemaName}.ProductID,
  ${ProductSchema.schemaName}.Name,
  ${ProductSchema.schemaName}.Price,
  ${ProductSchema.schemaName}.Image,
  ${Order_DetailsSchema.schemaName}.Amount
  from ${Order_DetailsSchema.schemaName}
  inner join ${ProductSchema.schemaName} on ${Order_DetailsSchema.schemaName}.ProductID = ${ProductSchema.schemaName}.ProductID
  inner join ${OrdersSchema.schemaName} o on ${Order_DetailsSchema.schemaName}.OrderID = o.OrderID
  where o.OrderID = @${Order_DetailsSchema.schema.OrderID.name} and o.UserID = @${OrdersSchema.schema.UserID.name}
  `;
  let result = await dbPool
    .request()
    .input(
      OrdersSchema.schema.OrderID.name,
      OrdersSchema.schema.OrderID.sqlType,
      orderid
    )
    .input(
      OrdersSchema.schema.UserID.name,
      OrdersSchema.schema.UserID.sqlType,
      userid
    )
    .query(query);
  return result.recordsets[0];
};

exports.updateStatusPayment = async (updateInfo) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  console.log("updateInfo", updateInfo);
  const orderID = updateInfo.OrderID;
  delete updateInfo.OrderID;
  const {request, updateStr} = dbUtils.getUpdateQuery(
    OrdersSchema.schema,
    dbConfig.db.pool.request(),
    updateInfo
  );
  const query = `update ${OrdersSchema.schemaName} set ${updateStr} where OrderID = @OrderID`;
  const result = await request
    .input(
      OrdersSchema.schema.OrderID.name,
      OrdersSchema.schema.OrderID.sqlType,
      orderID
    )
    .query(query);
  console.log(result);
};
exports.getOrderById = async (id) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  const dbPool = dbConfig.db.pool;
  const orderid = id;
  const query = `select  ${Order_DetailsSchema.schemaName}.OrderID,
  ${ProductSchema.schemaName}.ProductID,
  ${ProductSchema.schemaName}.Name,
  ${ProductSchema.schemaName}.Price,
  ${ProductSchema.schemaName}.Image,
  ${Order_DetailsSchema.schemaName}.Amount
  from ${Order_DetailsSchema.schemaName}
  inner join ${ProductSchema.schemaName} on ${Order_DetailsSchema.schemaName}.ProductID = ${ProductSchema.schemaName}.ProductID
  inner join ${OrdersSchema.schemaName} o on ${Order_DetailsSchema.schemaName}.OrderID = o.OrderID
  where o.OrderID = @${Order_DetailsSchema.schema.OrderID.name}
  `;
  let result = await dbPool
    .request()
    .input(
      OrdersSchema.schema.OrderID.name,
      OrdersSchema.schema.OrderID.sqlType,
      orderid
    )

    .query(query);
  return result.recordsets[0];
};

exports.deleteOrder = async (id) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }
  const resultQueryOrder = await dbPool
    .request()
    .input(
      OrdersSchema.schema.OrderID.name,
      OrdersSchema.schema.OrderID.sqlType,
      id
    )
    .query(`select * from ${OrdersSchema.schemaName} where OrderID = @OrderID`);

  const order = resultQueryOrder.recordset[0];
  if (order == null) {
    throw new Error("Order not found");
  }
  if (order.PayIn != null) {
    throw new Error("Order has been paid");
  }
  const queryDeleteOrderDetails = `delete ${Order_DetailsSchema.schemaName} where OrderID = @OrderID`;

  const queryDeleteOrder = `delete ${OrdersSchema.schemaName} where OrderID = @OrderID`;

  await dbPool
    .request()
    .input(
      OrdersSchema.schema.OrderID.name,
      OrdersSchema.schema.OrderID.sqlType,
      id
    )
    .query(queryDeleteOrderDetails);

  await dbPool
    .request()
    .input(
      OrdersSchema.schema.OrderID.name,
      OrdersSchema.schema.OrderID.sqlType,
      id
    )
    .query(queryDeleteOrder);
  if (order.UserID != null) {
    await this.createNewOrder(order.UserID);
  }
};

exports.clearAllOrder_Details = async () => {
  query = `delete ${Order_DetailsSchema.schemaName} ;`;
  let result = await dbConfig.db.pool.request().query(query);
  return result.recordsets;
};
exports.clearAllOrder = async () => {
  query = `delete ${OrdersSchema.schemaName}  DBCC CHECKIDENT ('[${OrdersSchema.schemaName} ]', RESEED, 1);`;
  let result = await dbConfig.db.pool.request().query(query);
  return result.recordsets;
};

exports.cancelOrder = async (id) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  const updateInfo = {
    OrderID: id,
    StatusID: 5,
  };
  const resultQueryOrder = await dbConfig.db.pool
    .request()
    .input(
      OrdersSchema.schema.OrderID.name,
      OrdersSchema.schema.OrderID.sqlType,
      id
    )
    .query(`select * from ${OrdersSchema.schemaName} where OrderID = @OrderID`);
  if (resultQueryOrder.recordset.length == 0) {
    throw new Error("Order not found");
  }
  if (resultQueryOrder.recordset[0].StatusID != 2) {
    throw new Error("Order can't cancel ");
  }
  await this.updateStatusPayment(updateInfo);
  //hupdate stok
  const orderDetails = await this.getOrderById(id);
  const updatePromises = orderDetails.map((element) =>
    ProductDAO.handleUpdateStock(element, true)
  );
  await Promise.all(updatePromises);
};
