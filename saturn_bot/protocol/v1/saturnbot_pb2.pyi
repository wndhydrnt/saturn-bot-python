# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExecuteActionsRequest(_message.Message):
    __slots__ = ("path", "context")
    PATH_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    path: str
    context: Context
    def __init__(self, path: _Optional[str] = ..., context: _Optional[_Union[Context, _Mapping]] = ...) -> None: ...

class ExecuteActionsResponse(_message.Message):
    __slots__ = ("error", "template_vars", "plugin_data")
    class TemplateVarsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class PluginDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_VARS_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_DATA_FIELD_NUMBER: _ClassVar[int]
    error: str
    template_vars: _containers.ScalarMap[str, str]
    plugin_data: _containers.ScalarMap[str, str]
    def __init__(self, error: _Optional[str] = ..., template_vars: _Optional[_Mapping[str, str]] = ..., plugin_data: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ExecuteFiltersRequest(_message.Message):
    __slots__ = ("context",)
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    context: Context
    def __init__(self, context: _Optional[_Union[Context, _Mapping]] = ...) -> None: ...

class ExecuteFiltersResponse(_message.Message):
    __slots__ = ("match", "error", "template_vars", "plugin_data")
    class TemplateVarsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class PluginDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    MATCH_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_VARS_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_DATA_FIELD_NUMBER: _ClassVar[int]
    match: bool
    error: str
    template_vars: _containers.ScalarMap[str, str]
    plugin_data: _containers.ScalarMap[str, str]
    def __init__(self, match: bool = ..., error: _Optional[str] = ..., template_vars: _Optional[_Mapping[str, str]] = ..., plugin_data: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetPluginRequest(_message.Message):
    __slots__ = ("config",)
    class ConfigEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _containers.ScalarMap[str, str]
    def __init__(self, config: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetPluginResponse(_message.Message):
    __slots__ = ("name", "priority", "error")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    name: str
    priority: int
    error: str
    def __init__(self, name: _Optional[str] = ..., priority: _Optional[int] = ..., error: _Optional[str] = ...) -> None: ...

class Context(_message.Message):
    __slots__ = ("repository", "pull_request", "plugin_data")
    class PluginDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    PULL_REQUEST_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_DATA_FIELD_NUMBER: _ClassVar[int]
    repository: Repository
    pull_request: PullRequest
    plugin_data: _containers.ScalarMap[str, str]
    def __init__(self, repository: _Optional[_Union[Repository, _Mapping]] = ..., pull_request: _Optional[_Union[PullRequest, _Mapping]] = ..., plugin_data: _Optional[_Mapping[str, str]] = ...) -> None: ...

class PullRequest(_message.Message):
    __slots__ = ("number", "web_url")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    WEB_URL_FIELD_NUMBER: _ClassVar[int]
    number: int
    web_url: str
    def __init__(self, number: _Optional[int] = ..., web_url: _Optional[str] = ...) -> None: ...

class Repository(_message.Message):
    __slots__ = ("full_name", "clone_url_http", "clone_url_ssh", "web_url")
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    CLONE_URL_HTTP_FIELD_NUMBER: _ClassVar[int]
    CLONE_URL_SSH_FIELD_NUMBER: _ClassVar[int]
    WEB_URL_FIELD_NUMBER: _ClassVar[int]
    full_name: str
    clone_url_http: str
    clone_url_ssh: str
    web_url: str
    def __init__(self, full_name: _Optional[str] = ..., clone_url_http: _Optional[str] = ..., clone_url_ssh: _Optional[str] = ..., web_url: _Optional[str] = ...) -> None: ...

class OnPrClosedRequest(_message.Message):
    __slots__ = ("context",)
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    context: Context
    def __init__(self, context: _Optional[_Union[Context, _Mapping]] = ...) -> None: ...

class OnPrClosedResponse(_message.Message):
    __slots__ = ("error",)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: str
    def __init__(self, error: _Optional[str] = ...) -> None: ...

class OnPrCreatedRequest(_message.Message):
    __slots__ = ("context",)
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    context: Context
    def __init__(self, context: _Optional[_Union[Context, _Mapping]] = ...) -> None: ...

class OnPrCreatedResponse(_message.Message):
    __slots__ = ("error",)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: str
    def __init__(self, error: _Optional[str] = ...) -> None: ...

class OnPrMergedRequest(_message.Message):
    __slots__ = ("context",)
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    context: Context
    def __init__(self, context: _Optional[_Union[Context, _Mapping]] = ...) -> None: ...

class OnPrMergedResponse(_message.Message):
    __slots__ = ("error",)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: str
    def __init__(self, error: _Optional[str] = ...) -> None: ...
