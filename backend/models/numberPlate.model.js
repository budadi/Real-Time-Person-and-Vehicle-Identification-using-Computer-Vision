const mongoose = require("mongoose");
const plateSchema = new mongoose.Schema({
  number: {
    type: String,
    required: true
  },
  Phone:{
    type:String,
   
  }
},
  {
    timestamps: true
  })


  const Plates = mongoose.model("Plates",plateSchema);
  
  module.exports = Plates;