class AuthApi {
  constructor(request) {
    this.request = request;
  }

  async register(userPayload) {
    return this.request.post('/users/register', { data: userPayload });
  }

  async login(email, password) {
    return this.request.post('/users/login', {
      data: { email, password }
    });
  }

  async registerAndLogin(userPayload) {
    const registerResponse = await this.register(userPayload);
    const loginResponse = await this.login(userPayload.email, userPayload.password);
    const loginBody = await loginResponse.json();

    return {
      registerResponse,
      loginResponse,
      accessToken: loginBody.access_token,
      user: userPayload
    };
  }
}

module.exports = { AuthApi };
