const CategoryDAO = require("../DAO/CategoryDAO");

exports.getAllCategories = async (req, res) => {
  try {
    let categories = await CategoryDAO.getCategories();
    res.status(200).json({
      Code: 200,
      Msg: null,
      Data: categories,
    });
  } catch (error) {
    res.status(404).json({
      Code: 404,
      Msg: error.toString(),
    });
  }
};

exports.getCateIdByName = async (req, res) => {
  // console.log("req.params", req.params);
  const name = req.params.categoryName;
  try {
    const category = await CategoryDAO.getCategoryIdByName(name);
    if (!category) {
      return res
        .status(404) //NOT FOUND
        .json({
          Code: 404,
          Msg: `Not found categoryID with name ${name}!`,
        });
    }
    return res.status(200).json({
      Code: 200,
      Msg: null,
      Data: category,
    });
  } catch (e) {
    console.log(e);
    return res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};
