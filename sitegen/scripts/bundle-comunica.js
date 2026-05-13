var qs = require('@comunica/query-sparql');
var c = globalThis.Comunica || {};
c.QueryEngine = qs.QueryEngine;
globalThis.Comunica = c;
