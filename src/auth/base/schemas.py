from pydantic import BaseModel, Field, SecretStr, field_validator, EmailStr


class LoginSchema(BaseModel):
    identifier: str = Field(..., min_length=3, max_length=50)
    password: SecretStr

    class Config:
        str_strip_whitespace = True


class RegisterSchema(BaseModel):
    # this model will validate when the dumped to UserCreate model
    # if you will use another model you should validate it like as UserCreate model validators
    username: str = Field(..., min_length=6, max_length=50)
    first_name: str = Field(..., min_length=3, max_length=50)
    last_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., min_length=3, max_length=50)
    password: SecretStr

    # password_repeat: SecretStr

    class Config:
        str_strip_whitespace = True


class ChangePassword(BaseModel):
    old_password: SecretStr
    new_password: SecretStr
    new_password_repeat: SecretStr

    @field_validator("new_password_repeat", mode="before")
    def password_match(cls, v, values, **kwargs):
        print(v)
        print(values.data)
        if "new_password" in values.data and v != values.data["new_password"].get_secret_value():
            raise ValueError("Şifreler eşleşmiyor.")
        return v
