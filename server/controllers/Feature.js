const FeatureDAO = require("../DAO/FeatureDAO");
const DTOFeature = require("../DTO/Default/DTOFeature");

exports.getFeatureById = async (req, res) => {
  const id = req.params.id * 1;
  try {
    const features = await FeatureDAO.getFeatureById(id);
    if (!features) {
      return res
        .status(404) //NOT FOUND
        .json({
          Code: 404,
          Msg: `Not found features with Id ${id}!`,
        });
    }
    return res.status(200).json({
      Code: 200,
      Msg: `Got features with id ${id} successfully!`,
      Data: features,
    });
  } catch (e) {
    console.log(e);
    return res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};
exports.getFeatures = async (req, res) => {
  try {
    let features;
    let id;
    if (req.query.ProductID) {
      id = req.query.ProductID * 1;
      features = await FeatureDAO.getFeaturesByProductId(id);
    } else {
      features = await FeatureDAO.getAllFeatures();
    }
    if (!features) {
      return res
        .status(404) //NOT FOUND
        .json({
          Code: 404,
          Msg: id
            ? `Not found features with productId ${id}!`
            : `Not found features!`,
        });
    }
    return res.status(200).json({
      Code: 200,
      Msg: id
        ? `Got features with productId ${id} successfully!`
        : `Got features successfully!`,
      Data: features,
    });
  } catch (e) {
    console.log(e);
    return res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};
exports.createNewFeature = async (req, res) => {
  const newFeature = req.body;
  const dto = new DTOFeature(newFeature);
  console.log(dto);
  try {
    await FeatureDAO.createNewFeature(dto);
    // console.log(`Created new product successfully!`);
    return res.status(200).json({
      Code: 200,
      Msg: null,
    });
  } catch (e) {
    console.log(e);
    res.status(500).json({
      Code: 500,
      Msg: `Feature create failed`,
    });
  }
};
exports.deleteFeatureById = async (req, res) => {
  const id = req.params.id * 1;
  try {
    const feature = await FeatureDAO.getFeatureById(id);
    if (!feature) {
      return res
        .status(404) //NOT FOUND
        .json({
          Code: 404,
          Msg: `Feature with Id ${id} not found!`,
        });
    }
    await FeatureDAO.deleteFeatureById(id);
    return res.status(200).json({
      Code: 200,
      Msg: null,
    });
  } catch (e) {
    console.log(e);
    return res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};
exports.updateFeatureById = async (req, res) => {
  const id = req.params.id * 1;
  try {
    const updateInfo = req.body;
    let feature = await FeatureDAO.getFeatureById(id);
    if (!feature) {
      return res.status(404).json({
        Code: 404,
        Msg: `Not found feature with Id ${id}!`,
      });
    }
    await FeatureDAO.updateFeatureById(id, updateInfo);
    feature = await FeatureDAO.getFeatureById(id);
    return res.status(200).json({
      Code: 200,
      Msg: `Updated feature with id: ${id} successfully!`,
      Data: feature,
    });
  } catch (e) {
    console.log(e);
    res.status(500).json({
      Code: 500,
      Msg: `Update feature with id: ${id} failed! ${e.toString()}`,
    });
  }
};
