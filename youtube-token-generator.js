const { generate } = require("./node-v22.13.1-win-x64/node_modules/youtube-po-token-generator");
generate().then(
  (token) => {
    console.log(JSON.stringify(token));
  },
  (error) => {
    console.error(error);
  }
);
