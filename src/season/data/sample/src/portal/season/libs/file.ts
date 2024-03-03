import Service from './service';
import $ from 'jquery';

export default class File {

    public filenode: any = null;

    constructor(private service: Service) { }

    public async resize(file, width, quality) {
        let fn: any = () => new Promise((resolve) => {
            if (!quality) quality = 0.8;
            if (!width) width = 64;

            let output = function (canvas, callback) {
                let blob = canvas.toDataURL('image/png', quality);
                callback(blob);
            }

            let _resize = function (dataURL, maxSize, callback) {
                let image = new Image();

                image.onload = function () {
                    let canvas = document.createElement('canvas'),
                        width = image.width,
                        height = image.height;
                    if (width > height) {
                        if (width > maxSize) {
                            height *= maxSize / width;
                            width = maxSize;
                        }
                    } else {
                        if (height > maxSize) {
                            width *= maxSize / height;
                            height = maxSize;
                        }
                    }
                    canvas.width = width;
                    canvas.height = height;
                    canvas.getContext('2d').drawImage(image, 0, 0, width, height);
                    output(canvas, callback);
                };

                image.onerror = function () {
                    return;
                };

                image.src = dataURL;
            };

            let photo = function (file, maxSize, callback) {
                let reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = function (readerEvent) {
                    _resize(readerEvent.target.result, maxSize, callback);
                };
            }

            photo(file, width, (blob) => {
                resolve(blob);
            });
        });

        return await fn();
    }

    public async upload(url: string, fd: any, callback: any = null) {
        let uploader = () => new Promise((resolve) => {
            $.ajax({
                url: url,
                type: 'POST',
                data: fd,
                cache: false,
                contentType: false,
                processData: false,
                xhr: () => {
                    let myXhr = $.ajaxSettings.xhr();
                    if (myXhr.upload) {
                        myXhr.upload.addEventListener('progress', async (event) => {
                            let percent = 0;
                            let position = event.loaded || event.position;
                            let total = event.total;
                            if (event.lengthComputable) {
                                percent = Math.round(position / total * 10000) / 100;
                                if (callback) await callback(percent, total, position);
                            }
                        }, false);
                    }
                    return myXhr;
                }
            }).always(function (res) {
                resolve(res);
            });
        });
        return await uploader();
    }

    public async drop($event) {
        $event.preventDefault();
        let getFilesWebkitDataTransferItems = (dataTransferItems) => {
            let files = [];

            function traverseFileTreePromise(item, path = '') {
                return new Promise(resolve => {
                    if (item.isFile) {
                        item.file(file => {
                            file.filepath = path + file.name //save full path
                            files.push(file)
                            resolve(file)
                        })
                    } else if (item.isDirectory) {
                        let dirReader = item.createReader();
                        const entriesPromises = [];
                        const readEntriesHandler = (entries) => {
                            if (entries.length === 0) {
                                resolve(Promise.all(entriesPromises));
                                return;
                            }
                            for (let entr of entries)
                                entriesPromises.push(traverseFileTreePromise(entr, path + item.name + "/"))
                            dirReader.readEntries(readEntriesHandler);
                        }
                        dirReader.readEntries(readEntriesHandler);
                    }
                })
            }

            return new Promise((resolve, reject) => {
                let entriesPromises = []
                for (let it of dataTransferItems)
                    entriesPromises.push(traverseFileTreePromise(it.webkitGetAsEntry()));

                Promise.all(entriesPromises)
                    .then(entries => {
                        resolve(files);
                    })
            })
        }

        return await getFilesWebkitDataTransferItems($event.dataTransfer.items);
    }

    public createFilenode(uopts: any = {}) {
        delete this.filenode;
        let opts: any = {
            accept: null,
            multiple: true
        };

        for (let key in uopts) {
            opts[key] = uopts[key];
        }

        let filenode = $(`<input type='file' ${opts.accept ? `accept='${opts.accept}'` : ''} ${opts.multiple ? 'multiple' : ''} />`);
        return filenode[0];
    }

    public async select(uopts: any = {}) {
        delete this.filenode;
        let opts: any = {
            type: 'file',
            accept: null,
            multiple: true
        };

        for (let key in uopts) {
            opts[key] = uopts[key];
        }

        let filenode = this.filenode = $(`<input type='file' ${opts.accept ? `accept='${opts.accept}'` : ''} ${opts.multiple ? 'multiple' : ''} />`);
        if (opts.type == 'folder') {
            filenode = this.filenode = $(`<input type='file' webkitdirectory mozdirectory msdirectory odirectory directory multiple/>`);
        }

        let fn: any = () => new Promise((resolve) => {
            filenode.change(async () => {
                let res = filenode.prop('files');
                filenode.remove();
                delete this.filenode;
                resolve(res);
            });

            filenode.click();
        });

        return await fn();
    }

    public async read(uopts: any = {}) {
        delete this.filenode;
        let opts: any = {
            type: 'text',  // text, image, json
            accept: null,
            multiple: null,
            width: 512,     // if image type
            quality: 0.8   // if image type
        };

        for (let key in uopts) {
            opts[key] = uopts[key];
        }

        let filenode = this.filenode = $(`<input type='file' ${opts.accept ? `accept='${opts.accept}'` : ''} ${opts.multiple ? 'multiple' : ''} />`);

        let result = {};

        result.text = () => new Promise((resolve) => {
            let targetLoader = (target) => new Promise((_resolve) => {
                let fr = new FileReader();
                fr.onload = async () => {
                    _resolve(fr.result);
                };
                fr.readAsText(target);
            });

            let loader = async () => {
                if (opts.multiple) {
                    let result = [];
                    let files = filenode.prop('files');
                    for (let i = 0; i < files.length; i++)
                        result.push(await targetLoader(files[i]));
                    return resolve(result);
                }

                resolve(await targetLoader(filenode.prop('files')[0]));
            }

            loader();
        });

        result.json = () => new Promise((resolve) => {
            let targetLoader = (target) => new Promise((_resolve) => {
                let fr = new FileReader();
                fr.onload = async () => {
                    let data = fr.result;
                    data = JSON.parse(data);
                    _resolve(data);
                };
                fr.readAsText(target);
            });

            let loader = async () => {
                if (opts.multiple) {
                    let result = [];
                    let files = filenode.prop('files');
                    for (let i = 0; i < files.length; i++)
                        result.push(await targetLoader(files[i]));
                    return resolve(result);
                }

                resolve(await targetLoader(filenode.prop('files')[0]));
            }

            loader();
        });

        result.image = async () => {
            let ifn: any = () => new Promise((resolve, reject) => {
                let file = filenode.prop('files')[0];
                if (!opts.width) opts.width = 512;
                if (!opts.quality) opts.quality = 0.8;
                if (opts.limit) {
                    if (file.length > opts.limit) {
                        reject("Exceeded maximum file size");
                    }
                }
                resolve(file);
            });

            let file = await ifn();
            file = await this.resize(file, opts.width, opts.quality);
            return file;
        }

        if (!result[opts.type]) opts.type = 'text';

        let fn: any = () => new Promise((resolve) => {
            filenode.change(async () => {
                let res = await result[opts.type]();
                filenode.remove();
                delete this.filenode;
                resolve(res);
            });

            filenode.click();
        });

        return await fn();
    }

    public async download(exportObj: any, exportName: string) {
        if (!exportName) exportName = 'download.json';
        let dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportObj));
        let downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", exportName);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    }

}