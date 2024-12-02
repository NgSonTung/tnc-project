const express = require("express");
const paymentController = require("../Controllers/Payment");
const authController = require("../Controllers/Auth");
const router = express.Router();
const StaticData = require("../Utils/StaticData");
const vnPayController = require("../Controllers/vnPay");

// role admin can access
router
  .route("/")
  .get(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    paymentController.getAllPayment
  )
  .post(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin)
    // paymentController.paymentpaymentController.updatePayment
  );

// role user can access
// router
//   .route("/paid")
//   .get(paymentController.payment)
//   .post(paymentController.paymentpaymentController.payment);

router.post("/handlerPayment", paymentController.handlerPayment);

router.get("/vnpayReturn", vnPayController.vnpay_return);

router.get("/vnpayIpn", vnPayController.vnpay_ipn);

module.exports = router;
