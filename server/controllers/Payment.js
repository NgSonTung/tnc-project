const PaymentDAO = require("../DAO/PaymentDAO");

exports.getAllPayment = async (req, res) => {
  try {
    const result = await PaymentDAO.getAllPayment();
    res.status(200).json({
      Code: 200,
      Msg: "OK",
      Data: {result},
    });
  } catch (e) {
    res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};

exports.handlerPayment = async (req, res) => {
  try {
    const {TypeOfPayment} = req.body;
    if (!TypeOfPayment) {
      throw new Error("Invalid parameter format");
    }
    delete req.body.TypeOfPayment;
    await PaymentDAO.handlerPayment(TypeOfPayment, req, res);
    // res.redirect("http://localhost:3001");
  } catch (e) {
    res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};
