
acl:
  type: object
  properties:
    uid:
      required: true
      description: is unique id for the acl, increments
      type: number
      format: int32
    aci:
      required: true
      description: list of access control items
      type: ACI[]
    hash:
      required: true
      description: md5 hash of concatenation of ACI hashes, used to find this acl to avoid duplicates
      type: text      

aci:
  type: object
  properties:
    uid:
      required: true
      description: is unique id for the acl, increments
      type: number
      format: int32  
    groups:
      required: false
      description: link to group(s)
      type: number[]
      format: int32
    users:
      required: false
      description: link to user(s)
      type: number[]
      format: int32
    right:
      required: true
      description: |
        text e.g. rwdl- (admin read write delete list -), freely to be chosen
        admin means all rights (e.g. on / = namespace or filesystem level all rights for everything)
        '-' means remove all previous ones (is to stop recursion), if group=0,user=0 then is for all users & all groups
      type: text
    hash:
      required: true
      description: md5 hash of id+sorted_groups+sorted_users+right, used to make sure we only link acl once
      type: text
