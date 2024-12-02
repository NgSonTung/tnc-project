const express = require("express");
const router = express.Router();
const orderController = require("../controllers/order");
const authController = require("../controllers/auth");
const StaticData = require("../utils/StaticData");
router
  .route("/product/")
  .get(orderController.getProductInOrderByUSerID)
  .patch(orderController.updateProductInOrder)
  .post(orderController.insertProductToOrder)
  .delete(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.user),
    orderController.deleteProductInOrder
  );

router
  .route("/orderdetails/")
  .get(orderController.getOrderDetailsByOrderIDUserID);

router.route("/:id").delete(orderController.deleteOrder);

router.route("/user/:UserID").get(orderController.getOrderByUserID);
// router.route("/:userID").get(orderController.getProductInCartByUSerID);

router.route("/test").post(orderController.updateStatusPayment);

router
  .route("/cancelorder/:id")
  .patch(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.user),
    orderController.cancelOrder
  );
module.exports = router;
