const DateTimeUtils = require("./DateTimeUtils");
exports.AUTH = {
  Role: {
    user: 3,
    admin: 2,
    master: 1,
  },
};

exports.config = {
  MAX_PAGE_SIZE: 20,
};
exports.DefaultTimeExpries = {
  TokenExpries: DateTimeUtils.convertToMilliseconds(process.env.JWT_EXPIRED_IN),
  RefreshTokenExpries: DateTimeUtils.convertToMilliseconds(
    process.env.REFRESH_JWT_EXPRIRED_IN
  ),
};

exports.configApiVnPay = {
  vnp_TmnCode: "84KHKVDO",
  vnp_HashSecret: "IZHDEWTGNCBLZLAYJGHNIMXWRXNEHMOQ",
  vnp_Url: "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
  vnp_Api: "https://sandbox.vnpayment.vn/merchant_webapi/api/transaction",
  vnp_ReturnUrl: "http://localhost:3001/api/v1/payment/vnpayReturn",
  home_Url: "http://localhost:4200",
};
