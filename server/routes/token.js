const express = require("express");
const authController = require("../controllers/auth");
const router = express.Router();
const StaticData = require("../utils/StaticData");
router.route("/dev").get(authController.getTokenDev);

router.route("/refreshtoken").post(authController.getRefreshToken);
router
  .route("/refreshtoken/clean")
  .delete(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    authController.cleanRToken
  );
module.exports = router;
