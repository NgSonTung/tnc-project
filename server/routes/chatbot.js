const express = require("express");
const ChatBoxController = require("../Controllers/ChatBot");
const router = express.Router();
const StaticData = require("../utils/StaticData");

router.route("/").get(ChatBoxController.getSession);
router.route("/:id").get(ChatBoxController.getSessionID);
router.route("/chat/:id").post(ChatBoxController.addChat);

router.route("/image/:imageName").get(ChatBoxController.getImage);
// router.route("/").get(FeatureController.getFeatureByProductId);

module.exports = router;
