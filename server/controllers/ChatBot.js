const axios = require("axios");
exports.getSession = async (req, res) => {
  try {
    const response = await axios.get("http://127.0.0.1:5000/api/v1/session");

    const data = response;

    res.status(200).json(data);
  } catch (error) {
    console.error("Error sending request:", error);
    res
      .status(500)
      .json({ error: "An error occurred while sending the request." });
  }
};

exports.getSessionID = async (req, res) => {
  try {
    const response = await axios.get(
      "http://127.0.0.1:5000/api/v1/session/647f3c5170b47d535c175512"
    );

    const data = response;

    res.status(200).json(data.data);
  } catch (error) {
    console.error("Error sending request:", error);
    res
      .status(500)
      .json({ error: "An error occurred while sending the request." });
  }
};

exports.addChat = async (req, res) => {
  try {
    const reqBody = req.body.msg;
    console.log(req);
    console.log("EEEEEEE", reqBody);
    const response = await axios.post(
      "http://127.0.0.1:5000/api/v1/chat",
      reqBody
    );

    const data = response;

    res.status(200).json(data.data);
  } catch (error) {
    console.error("Error sending request:", error);
    res
      .status(500)
      .json({ error: "An error occurred while sending the request." });
  }
};

exports.getImage = async (req, res) => {
  try {
    const imageName = req.params.imageName;
    const response = await axios.get(
      "http://127.0.0.1:5000/api/v1/chat/image/" + imageName,
      {
        responseType: "blob",
      }
    );

    const data = response;

    res.status(200).json(data);
  } catch (error) {
    console.error("Error sending request:", error);
    res
      .status(500)
      .json({ error: "An error occurred while sending the request." });
  }
};
