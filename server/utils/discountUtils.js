const money2PointsRate = 0.000001;
const points2MoneyRate = 100000;

exports.getPoint = (total) => total * money2PointsRate;

exports.getDiscount = (points) => points * points2MoneyRate;
