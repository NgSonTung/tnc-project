const OrderDAO = require("../DAO/OrderDAO");
const DTOOrderDetails = require("../DTO/Default/DTOOrderDetails");

//order details

exports.getProductInOrderByUSerID = async (req, res) => {
  try {
    let result = await OrderDAO.getProductInOderByUserID(req.query.UserID);
    res.status(200).json({
      Code: 200,
      Msg: null,
      Data: {
        TotalAmount: result.TotalAmount,
        OrderID: result.OrderID,
        StatusID: result.StatusID,
        DataInOrder: result.DataInOrder,
      },
    });
  } catch (error) {
    res.status(404).json({
      Code: 404,
      Msg: error.toString(),
    });
  }
};

exports.getOrderDetailsByOrderIDUserID = async (req, res) => {
  try {
    const reqHeaders = req.headers;
    let result = await OrderDAO.getOrderDetailsByOrderIDUserID(reqHeaders);
    res.status(200).json({
      Code: 200,
      Msg: null,
      Data: result,
    });
  } catch (error) {
    res.status(404).json({
      Code: 404,
      Msg: error.toString(),
    });
  }
};

// exports.createNewCart = async(req,res)=>{
//   try {
//     let result = await OrderDAO.createNewCart(req.params.userID);
//     res.status(200).json({
//       Code: 200,
//       Msg: "OK",
//       data: {
//         result,
//       },
//     });
//   } catch (error) {
//     res.status(404).json({
//       Code: 404,
//       Msg: "FAIL",
//     });
//   }
// }

exports.insertProductToOrder = async (req, res) => {
  // console.log(req.body);
  const dto = new DTOOrderDetails(req.body);
  try {
    let result = await OrderDAO.addOrder_DetailsIfNotExisted(dto);
    res.status(200).json({
      Code: 200,
      Msg: null,
      Data: result,
    });
  } catch (error) {
    res.status(404).json({
      Code: 404,
      Msg: error.toString(),
    });
  }
};

exports.updateProductInOrder = async (req, res) => {
  const dto = new DTOOrderDetails(req.body);
  console.log(dto);

  try {
    let result = await OrderDAO.updateOrder_Details(dto);
    res.status(200).json({
      Code: 200,
      Msg: null,
      Data: result,
    });
  } catch (error) {
    res.status(404).json({
      Code: 404,
      Msg: error.toString(),
    });
  }
};

exports.deleteProductInOrder = async (req, res) => {
  const q = req.query;
  try {
    let result = await OrderDAO.deleteItemInOrder(q, req.user);
    res.status(200).json({
      Code: 200,
      Msg: null,
    });
  } catch (error) {
    res.status(404).json({
      Code: 404,
      Msg: error.toString(),
    });
  }
};

// order

exports.getOrderByUserID = async (req, res) => {
  const r = req.params.UserID * 1;
  console.log(r);
  try {
    let result = await OrderDAO.getOrderByUserID(r);
    res.status(200).json({
      Code: 200,
      Msg: null,
      Data: result,
    });
  } catch (error) {
    res.status(404).json({
      Code: 404,
      Msg: error.toString(),
    });
  }
};

exports.updateStatusPayment = async (req, res) => {
  try {
    let result = await OrderDAO.updateStatusPayment(req.body);
    res.status(200).json({
      Code: 200,
      Msg: null,
      Data: result,
    });
  } catch (error) {
    res.status(404).json({
      Code: 404,
      Msg: error.toString(),
    });
  }
};

exports.deleteOrder = async (req, res) => {
  const id = req.params.id * 1;
  try {
    let result = await OrderDAO.deleteOrder(id);
    res.status(200).json({
      Code: 200,
      Msg: null,
    });
  } catch (error) {
    res.status(404).json({
      Code: 404,
      Msg: error.toString(),
    });
  }
};

exports.cancelOrder = async (req, res) => {
  const id = req.params.id * 1;
  try {
    let result = await OrderDAO.cancelOrder(id);
    res.status(200).json({
      Code: 200,
      Msg: null,
    });
  } catch (error) {
    res.status(404).json({
      Code: 404,
      Msg: error.toString(),
    });
  }
};
