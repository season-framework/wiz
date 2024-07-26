import season
import subprocess

class Model:
    @staticmethod
    def execute(cmd, log=True):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        
        logger = wiz.logger('build')
        if log:
            if out is not None and len(out) > 0: 
                out = out.decode('utf-8').strip()
                wiz.logger('build/log')(out)
            if err is not None and len(err) > 0: 
                err = err.decode('utf-8').strip()
                if "npm WARN" in err or "- Installing packages (npm)" in err:
                    wiz.logger('build/log')(err, level=season.LOG_WARNING)
                else: 
                    wiz.logger('build/error')(err, level=season.LOG_CRITICAL)

    @staticmethod
    def is_working(fs, timestamp):
        try:
            if fs.exists("build/working"):
                timestampLog = int(fs.read("build/working"))
                if timestamp - timestampLog < 5000:
                    fs.write("build/working", str(timestamp))
                    return True
        except:
            return True
        fs.write("build/working", str(timestamp))
        return False

    @staticmethod
    def is_work_finish(fs, timestamp):
        if fs.exists("build/working"):
            timestampLog = int(fs.read("build/working"))
            fs.remove("build/working")
            if timestamp < timestampLog:
                return False
        return True