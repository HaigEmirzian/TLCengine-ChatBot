//Imports csv data into the censusdata mongodb collection
//Usage: node csv-importer.js

const fs = require('fs');
const csv = require('csv-parser');
const { MongoClient } = require('mongodb');

//Change your <PASSWORDHERE> to your mongodb pwd
const uri = "mongodb+srv://bsampson:<PASSWORDHERE>@seniordesigncluster.r32ch.mongodb.net/?retryWrites=true&w=majority&appName=SeniorDesignCluster";
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });

async function importCSV() {
    try {
        await client.connect();
        const database = client.db("CensusData");
        const collection = database.collection("CensusData");

        const dataArray = [];
        fs.createReadStream('ACSDP5Y2022.DP05-Data.csv')
            .pipe(csv())
            .on('data', (row) => {
                dataArray.push(row);
            })
            .on('end', async () => {
                const result = await collection.insertMany(dataArray);
                console.log(`${result.insertedCount} documents were inserted`);
                client.close();
            });
    } catch (error) {
        console.error("Error importing CSV:", error);
    }
}

importCSV();
