const brandDAO = require("../DAO/BrandDAO");

exports.getAllBrands = async (req, res) => {
  try {
    let brands = await brandDAO.getBrands();
    res.status(200).json({
      Code: 200,
      Msg: null,
      Data: brands,
    });
  } catch (error) {
    res.status(404).json({
      Code: 404,
      Msg: error.toString().toString(),
    });
  }
};

exports.getBrandById = async (req, res) => {
  // console.log("req.params", req.params);
  const id = req.params.id * 1;
  try {
    const brand = await brandDAO.getBrandById(id);
    if (!brand) {
      return res
        .status(404) //NOT FOUND
        .json({
          Code: 404,
          Msg: `Not found brand with Id ${id}!`,
        });
    }
    return res.status(200).json({
      Code: 200,
      Msg: null,
      Data: brand,
    });
  } catch (e) {
    console.log(e);

    return res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};
