const mmcache = require("macrometa-realtime-cache"); 

// Initialize
const cache = new mmcache({
  url: "https://gdn.paas.macrometa.io",
  apiKey: "XXXX",
  ttl: 120,
});
await cache.create("sampleCache");

// Set the value
cache.set("cacheKey", { foo: "bar" }, 120, function (error, data) {
  if (error) throw data.errorMessage;

  // get the value
  cache.get("cacheKey", function (error, data) {
    if (error) throw data.errorMessage;

    // delete entry
    cache.delete("cacheKey", function (error, data) {
      if (error) throw data.errorMessage;

    });
  });
});





