import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }
    public async ngOnInit() {
        await this.service.init();
        await this.service.auth.allow(false, '/main');
        await this.service.render();
    }

    public step: number = -1;

    public async move(step: number = 0) {
        this.step = step;
        await this.service.render();
    }

    // 이메일 인증
    public status: any = 0;

    public data: any = {
        mail: '',
        code: ''
    };

    public async alert(message: string, status: string = 'error') {
        return await this.service.alert.show({
            title: "",
            message: message,
            cancel: false,
            actionBtn: status,
            action: "확인",
            status: status
        });
    }

    public async check(mail: any) {
        let { code, data } = await wiz.call("check", { mail });
        if (code == 200) {
            this.status = 1;
            await this.service.render();
            return;
        }
        await this.alert(data);
    }

    public async resend(mail: any) {
        let { code, data } = await wiz.call("resend", { mail });
        if (code == 200) {
            await this.alert("인증번호가 전송되었습니다.", "success")
            return;
        }
        await this.alert(data);
    }

    public async verify(mail: any, vcode: any) {
        let { code, data } = await wiz.call("verify", { mail, code: vcode });
        if (code == 200) {
            await this.alert("인증되었습니다. 회원가입 절차를 진행해주세요.", "success");
            await this.service.auth.init();
            if (!this.service.auth.session.verified)
                return;
            
            this.data.mail = this.service.auth.session.verified;
            await this.service.render();
            this.move(0);
            return;
        }
        await this.alert(data);
    }

    // 회원가입
    public userdata: any = {
        mail: '',
        name: '',
        password: '',
        password_repeat: '',
        tel: '',
        mobile: '',
        fax: '',
        institute: '',
        department: '',
        title: ''
    };

    public async step1() {
        if (this.userdata.name.length == 0) return await this.alert("이름을 입력해주세요");
        if (this.userdata.tel.length == 0) return await this.alert("연락처를 입력해주세요");
        if (this.userdata.mobile.length == 0) return await this.alert("휴대폰 번호를 입력해주세요");
        this.step = 1;
        await this.service.render();
    }

    public async step2() {
        this.step = 2;
        await this.service.render();
    }

    public async join() {
        let password = this.userdata.password;
        let password_re = this.userdata.password_repeat;

        if (password.length < 8) return await this.alert("8글자 이상의 비밀번호를 설정해주세요");
        if (password.search(/[a-z]/i) < 0) return await this.alert("비밀번호에 알파벳을 포함해주세요");
        if (password.search(/[0-9]/) < 0) return await this.alert("비밀번호에 숫자를 포함해주세요");
        if (password != password_re) return await this.alert("비밀번호가 일치하지 않습니다");

        let user = JSON.parse(JSON.stringify(this.userdata));
        delete user.password_repeat;

        user.password = this.service.auth.hash(user.password);

        let { code } = await wiz.call("join", user);

        if (code != 200) {
            await this.alert("잘못된 접근입니다");
            location.href = "/";
        }

        await this.alert("회원가입이 완료되었습니다. 로그인을 해주세요.", "success");
        location.href = "/auth/login";
    }
}