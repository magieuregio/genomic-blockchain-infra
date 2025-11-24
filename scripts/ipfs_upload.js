const { create } = require('ipfs-http-client');
const fs = require('fs');
const path = require('path');

const ipfs = create({ url: 'https://ipfs.infura.io:5001/api/v0' });


async function uploadFile(filepath) {
    const file = fs.readFileSync(filepath);
    const { cid } = await ipfs.add({ path: path.basename(filepath), content: file });
    console.log(`${filepath} -> ${cid}`);
    return cid.toString();
}

async function uploadFolder(folder) {
    const files = fs.readdirSync(folder);
    for (const file of files) {
        if (!file.endsWith('.json') && !file.endsWith('.bin')) continue; // Only upload relevant files
        await uploadFile(path.join(folder, file));
    }
}

if (require.main === module) {
    const folder = process.argv[2];
    if (!folder) {
        console.log('Usage: node scripts/ipfs_upload.js <folder>');
        process.exit(1);
    }
    uploadFolder(folder);
}
