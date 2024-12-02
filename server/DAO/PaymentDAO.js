const PaymentSchema = require("../model/Payment");
const dbConfig = require("../database/dbconfig");

const dbUtils = require("../utils/dbUtils");
const DateTimeUtils = require("../utils/DateTimeUtils");
const discountUtils = require("../utils/discountUtils");

const vnPayController = require("../controllers/vnPay");
const OrderDAO = require("../DAO/OrderDAO");
const UserDAO = require("../DAO/UserDAO");
const ProductDAO = require("../DAO/ProductDAO");

exports.addPaymentIfNotExists = async (payment) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }
  const ms = DateTimeUtils.convertDateTimeToMilliseconds(Date.now());
  payment.CreatedAt = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);

  let insertData = PaymentSchema.validateData(payment);
  let query = `SET IDENTITY_INSERT ${PaymentSchema.schemaName} ON insert into ${PaymentSchema.schemaName}`;
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(PaymentSchema.schema, dbPool.request(), insertData);
  if (!insertFieldNamesStr || !insertValuesStr) {
    throw new Error("Invalid insert param");
  }

  query +=
    " (" +
    insertFieldNamesStr +
    ") select  " +
    insertValuesStr +
    ` WHERE NOT EXISTS(SELECT * FROM ${PaymentSchema.schemaName} WHERE PaymentName = @paymentName)` +
    ` SET IDENTITY_INSERT ${PaymentSchema.schemaName} OFF`;
  let result = await request.query(query);
  return result.recordsets;
};

exports.getAllPayment = async () => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  const query = `
  select * from ${PaymentSchema.schemaName}
  `;
  let result = await dbConfig.db.pool.request().query(query);
  return result.recordsets[0];
};

exports.clearAll = async () => {
  query = `delete ${PaymentSchema.schemaName}  DBCC CHECKIDENT ('[${PaymentSchema.schemaName} ]', RESEED, 1);`;
  let result = await dbConfig.db.pool.request().query(query);
  return result.recordsets;
};

exports.handlerPayment = async (TypeOfPayment, req, res) => {
  const reqBody = req.body;
  if (!reqBody) {
    throw new Error("Invalid parameter format");
  }
  let order;
  let user;
  if (reqBody.OrderID) {
    order = await OrderDAO.getOrderById(req.body.OrderID);
    user = await UserDAO.getUserByOrderID(req.body.OrderID);
  }
  let orderID;
  if (reqBody?.DataInOrder || reqBody?.DataInOrder?.length > 0) {
    //handle cho khach hang vang lai

    order = reqBody.DataInOrder;
    user = reqBody.UserInfor;
    orderID = await OrderDAO.createNewOrder(null);
    //insert order detail
    for (let i = 0; i < order.length; i++) {
      const orderDetail = {
        OrderID: orderID,
        ProductID: order[i].ProductID,
        Amount: order[i].Amount,
        Price: order[i].Price,
      };
      await OrderDAO.addOrder_DetailsIfNotExisted(orderDetail);
    }
  }

  const totalPrice = order.reduce(
    (accumulator, product) => accumulator + product.Price * product.Amount,
    0
  );
  if (reqBody.UserPoint && reqBody.OrderID) {
    //update point for user
    const updateInfor = {
      UserID: user.UserID,
      Point: discountUtils.getPoint(totalPrice),
    };
    await UserDAO.updateUserById(user.UserID, updateInfor);
    //handle giam gia cho khach hang
    totalPrice -= discountUtils.getDiscount(user.Point);
  }

  req.body.TotalPrice = totalPrice;
  req.body.OrderID = orderID || req.body.OrderID;
  if (TypeOfPayment === "VNPAY") {
    vnPayController.create_payment_url(req, res);
  } else if (TypeOfPayment === "COD") {
    const updateInfor = {
      OrderID: req.body.OrderID,
      PaymentID: 1,
      StatusID: 2,
      PayIn: DateTimeUtils.convertMillisecondsToDateTimeSQL(
        1,
        false,
        true,
        true
      ),
    };
    await OrderDAO.updateStatusPayment(updateInfor);
    //update stock

    const result2 = await OrderDAO.getOrderById(req.body.OrderID);

    const updatePromises = result2.map((element) =>
      ProductDAO.handleUpdateStock(element)
    );
    await Promise.all(updatePromises);
    if (user) {
      await OrderDAO.createNewOrder(user.UserID);
    }
    res
      .status(200)
      .json({PaymentUrl: "http://localhost:3001/html/success.html"});
  } else {
    throw new Error("Invalid type of payment method");
  }
};
