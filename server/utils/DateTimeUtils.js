const moment = require("moment-timezone");

/**
 * convert h,m,s to ms
 */
exports.convertToMilliseconds = (param) => {
  const regex = /^(\d+)([hms])$/; // Regular expression to match the numeric value and unit
  const match = param.match(regex);

  if (!match) {
    throw new Error("Invalid parameter format");
  }

  const value = parseInt(match[1], 10);
  const unit = match[2];

  let milliseconds;

  switch (unit) {
    case "h":
      milliseconds = value * 60 * 60 * 1000; // Convert hours to milliseconds
      break;
    case "m":
      milliseconds = value * 60 * 1000; // Convert minutes to milliseconds
      break;
    case "s":
      milliseconds = value * 1000; // Convert seconds to milliseconds
      break;
    default:
      throw new Error("Invalid unit");
  }

  return milliseconds;
};

/**
 * convert ms to datetime (sql format)
 */
exports.convertMillisecondsToDateTimeSQL = (
  ms,
  jwtExp = false,
  add7h = true,
  combineDateNow = false
) => {
  if (combineDateNow) {
    ms += this.convertDateTimeToMilliseconds(new Date().toISOString());
  }
  if (jwtExp) {
    ms = ms * 1000;
  }
  if (add7h) {
    ms += this.convertToMilliseconds("7h");
  }
  const converted = moment(ms).toISOString();
  const vnDateTimeString = moment(converted)
    .tz("Asia/Ho_Chi_Minh")
    .format("YYYY-MM-DD HH:mm:ss");

  return vnDateTimeString;
};

/**
 * convert date time to ms
 */
exports.convertDateTimeToMilliseconds = (dateTime) => {
  const converted = moment(dateTime).tz("Asia/Ho_Chi_Minh").format();
  const ms = moment(converted).valueOf();
  return ms;
};

/**
 * calculate time difference
 * getBoolen: return true if end > start else return false
 */
exports.calculateTimeDifference = (start, end, getBoolen = false) => {
  const startMs = this.convertDateTimeToMilliseconds(start);
  const endMs = this.convertDateTimeToMilliseconds(end);
  const diff = endMs - startMs;
  if (getBoolen) {
    return diff > 0;
  }
  return diff;
};

/**
 * convert date time to YYYY-MM-DD HH:mm:ss format
 **/
exports.convertSqlDateTimeToUIDateTime = (sqlDateTime) => {
  const converted = moment(sqlDateTime).format("DD-MM-YYYY HH:mm:ss");
  return converted;
};
