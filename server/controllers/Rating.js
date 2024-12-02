const RatingDAO = require("../DAO/RatingDAO");
const DTORating = require("../DTO/Default/DTORating");
exports.getRatingById = async (req, res) => {
  // console.log(req.params);
  const id = req.params.id * 1;
  try {
    const rating = await RatingDAO.getRatingById(id);
    if (!rating) {
      return res
        .status(404) //NOT FOUND
        .json({
          Code: 404,
          Msg: `Not found rating with Id ${id}!`,
        });
    }

    return res.status(200).json({
      Code: 200,
      Msg: null,
      Data: rating,
    });
  } catch (e) {
    console.log(e);
    return res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};

exports.getRatings = async (req, res) => {
  try {
    let rating;
    let id;
    if (req.query.productId) {
      id = req.query.productId * 1;
      rating = await RatingDAO.getRatingByProductId(id);
    } else {
      rating = await RatingDAO.getAllRatings();
    }
    if (!rating) {
      return res
        .status(404) //NOT FOUND
        .json({
          Code: 404,
          Msg: id
            ? `Not found ratings with productId ${id}!`
            : `Not found ratings!`,
        });
    }
    return res.status(200).json({
      Code: 200,
      Msg: null,
      Data: rating,
    });
  } catch (e) {
    console.log(e);
    return res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};

exports.createNewRating = async (req, res) => {
  const newRating = req.body;
  try {
    await RatingDAO.createNewRating(newRating);
    return res.status(200).json({
      Code: 200,
      Msg: null,
    });
  } catch (e) {
    console.log(e);
    res.status(500).json({
      Code: 500,
      Msg: `Create new rating failed!`,
    });
  }
};

exports.deleteRatingById = async (req, res) => {
  const id = req.params.id * 1;
  try {
    const rating = await RatingDAO.getRatingById(id);
    if (!rating) {
      return res
        .status(404) //NOT FOUND
        .json({
          Code: 404,
          Msg: `Rating with Id ${id} not found!`,
        });
    }
    await RatingDAO.deleteRatingById(id);
    return res.status(200).json({
      Code: 200,
      Msg: null,
    });
  } catch (e) {
    console.log(e);
    return res.status(500).json({
      Code: 500,
      Msg: `Delete rating with id ${id} failed! ${e.toString()}`,
    });
  }
};

exports.updateRatingById = async (req, res) => {
  // console.log("Id update", req.params.id);
  try {
    const reqBody = req.body;
    const updateInfo = new DTORating(reqBody);
    const productID = updateInfo.ProductID;
    delete updateInfo.ProductID;
    // console.log(updateInfo);
    await RatingDAO.updateRatingById(productID, updateInfo);
    rating = await RatingDAO.getRatingByProductId(productID);
    return res.status(200).json({
      Code: 200,
      Msg: null,
      Data: rating,
    });
  } catch (e) {
    console.log(e);
    res.status(500).json({
      Code: 500,
      Msg: `Update rating with id failed! ${e.toString()}`,
    });
  }
};
