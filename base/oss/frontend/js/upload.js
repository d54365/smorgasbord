//分片大小 5m
const chunkSize = 5 * 1024 * 1024;


/**
 * 注意：本测试Demo不受分片顺序影响
 * 关于上传文件成功后的处理：配置minio监听指定存储桶指定格式文件上传成功后，push通知到mq,后端程序监听并消费即可
 * （建议上传mp4，成功后可以直接在页面看到效果）
 * 测试分片上传
 *      运行页面 > 打开控制台 > console > 选择上传的文件 > 观察打印的信息
 * 测试秒传
 *      在上一个测试的基础上，刷新一下页面，选择上一次上传的文件
 * 测试断点续传
 *      重新选择一个文件(如果你没有多的测试文件，就重启一下后台服务) > 手动模拟上传了一部分失败的场景(在所有分片未上传完成时关掉页面 或 注释掉合并文件代码，然后去 minio chunk桶 删除几个分片)
 *      > 再选择刚选择的文件上传 > 观察打印的信息是否从缺失的分片开始上传
 */
uploadFile = async () => {
    //获取用户选择的文件
    const file = document.getElementById("upload").files[0];
    //文件大小(大于5m再分片哦，否则直接走普通文件上传的逻辑就可以了，这里只实现分片上传逻辑)
    const fileSize = file.size

    if (fileSize <= chunkSize){
        console.log("上传的文件大于5m才能分片上传")
        return
    }

    //计算当前选择文件需要的分片数量
    const chunkCount = Math.ceil(fileSize / chunkSize)
    console.log("文件大小：",(file.size / 1024 / 1024) + "Mb","分片数：",chunkCount)

    //获取文件md5
    const fileMd5 = await getFileMd5(file);
    console.log("文件md5：",fileMd5)

    console.log("向后端请求本次分片上传初始化")
    //向后端请求本次分片上传初始化
    const initUploadParams = JSON.stringify({chunk_count: chunkCount,file_name: file.name})
    $.ajax({url: "http://127.0.0.1:8000/api/account/v1/multipart/create/", type: 'POST', contentType: "application/json", processData: false, data: initUploadParams,
        success: async function (res) {
            console.log("当前文件上传情况：初次上传 或 断点续传")
            const chunkUploadUrls = res.chunks

            for (item of chunkUploadUrls) {
                //分片开始位置
                let start = (item.part_number) * chunkSize
                //分片结束位置
                let end = Math.min(fileSize, start + chunkSize)
                //取文件指定范围内的byte，从而得到分片数据
                console.log(start, end)
                let _chunkFile = file.slice(start, end)
                console.log("开始上传第" + item.part_number + "个分片")
                await $.ajax({url: item.upload_url, type: 'PUT', contentType: false, processData: false, data: _chunkFile,
                    success: function (res) {
                        console.log("第" + item.part_number + "个分片上传完成")
                    }
                })
            }
            //请求后端合并文件
            composeFile(res.upload_id, res.object_name, chunkCount, fileSize, file.contentType)
        }
    })
}
/**
 * 请求后端合并文件
 * @param fileMd5
 * @param fileName
 */
composeFile = (uploadId,fileName, chunkSize, fileSize, contentType) => {
    console.log("开始请求后端合并文件")
    //注意：bucketName请填写你自己的存储桶名称，如果没有，就先创建一个写在这
    const composeParams = JSON.stringify({upload_id: uploadId,object_name: fileName,chunkSize: chunkSize, fileSize: fileSize, contentType: contentType, expire: 12, maxGetCount: 2})
    $.ajax({url: "http://127.0.0.1:8000/api/account/v1/multipart/complete/", type: 'POST', contentType: "application/json", processData: false, data: composeParams,
        success: function (res) {
            console.log("合并文件完成",res)
        }
    })
}

/**
 * 获取文件MD5
 * @param file
 * @returns {Promise<unknown>}
 */
getFileMd5 = (file) => {
    let fileReader = new FileReader()
    fileReader.readAsBinaryString(file)
    let spark = new SparkMD5()
    return new Promise((resolve) => {
        fileReader.onload = (e) => {
            spark.appendBinary(e.target.result)
            resolve(spark.end())
        }
    })
}
