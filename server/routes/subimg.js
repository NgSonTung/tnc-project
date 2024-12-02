const express = require("express");
const SubImageController = require("../controllers/Subimg");
const router = express.Router();
const authController = require("./../controllers/auth");
const StaticData = require("../utils/StaticData");

router
  .route("/:id")
  .get(SubImageController.getSubImages)
  .delete(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    SubImageController.deleteSubImgById
  )
  .patch(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    SubImageController.updateSubImgById
  );

router
  .route("/")
  .get(SubImageController.getSubImages)
  .post(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    SubImageController.createNewSubImg
  );

// router.route("/byProduct/:id").get(SubImageController.getSubImgByProductId);
router
  .route("/image")
  .post(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    SubImageController.saveFileSubImage
  );
router
  .route("/product/:id")
  .get(SubImageController.getFileSubImage)
  .delete(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    SubImageController.deleteFileSubImage,
    SubImageController.deleteSubImgById
  );

// router.route("/saveFileImage").post(SubImageController.saveFileImage);
module.exports = router;
