const express = require("express");
const FeatureController = require("../controllers/Feature");
const router = express.Router();
const authController = require("./../controllers/auth");
const StaticData = require("../utils/StaticData");

router
  .route("/:id")
  .get(FeatureController.getFeatureById)
  .delete(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    FeatureController.deleteFeatureById
  )
  .patch(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    FeatureController.updateFeatureById
  );

router
  .route("/")
  .get(FeatureController.getFeatures)
  .post(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    FeatureController.createNewFeature
  );
// router.route("/").get(FeatureController.getFeatureByProductId);

module.exports = router;
