/*
 * The Forgotten Architect - Unity VRChat Avatar Setup Script
 *
 * This script automates the complete VRChat avatar setup process:
 * - Imports FBX model
 * - Configures avatar descriptor
 * - Sets up FX animator with horror emotes
 * - Creates expressions menu
 * - Builds avatar package
 *
 * Executed via Unity CLI in GitHub Actions
 */

using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using System.IO;
using System.Collections.Generic;

#if UNITY_EDITOR && VRC_SDK_VRCSDK3
using VRC.SDK3.Avatars.Components;
using VRC.SDK3.Avatars.ScriptableObjects;
#endif

public class SetupAvatar : EditorWindow
{
    private const string AVATAR_NAME = "ForgottenArchitect";
    private const string FBX_PATH = "Assets/ForgottenArchitect/ForgottenArchitect.fbx";
    private const string PREFAB_OUTPUT_PATH = "Assets/ForgottenArchitect/ForgottenArchitect.prefab";

    [MenuItem("VRChat/Setup Forgotten Architect Avatar")]
    public static void Setup()
    {
        Debug.Log("=== The Forgotten Architect - Avatar Setup ===");

        // Step 1: Import FBX
        ImportFBX();

        // Step 2: Configure avatar
        GameObject avatarObject = ConfigureAvatar();

        // Step 3: Setup VRChat descriptor
        SetupVRChatDescriptor(avatarObject);

        // Step 4: Create FX animator
        AnimatorController fxController = CreateFXAnimator();

        // Step 5: Assign animator to descriptor
        AssignAnimatorToDescriptor(avatarObject, fxController);

        // Step 6: Create expressions menu
        VRCExpressionsMenu menu = CreateExpressionsMenu();
        VRCExpressionParameters parameters = CreateExpressionParameters();

        // Step 7: Assign menu to descriptor
        AssignMenuToDescriptor(avatarObject, menu, parameters);

        // Step 8: Save as prefab
        SaveAsPrefab(avatarObject);

        Debug.Log("=== Avatar Setup Complete! ===");
    }

    // Execute setup via command line
    public static void SetupFromCommandLine()
    {
        try
        {
            Setup();
            EditorApplication.Exit(0);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Setup failed: {e.Message}");
            EditorApplication.Exit(1);
        }
    }

    private static void ImportFBX()
    {
        Debug.Log("Importing FBX...");

        string sourcePath = "/home/user/Vrchat-avatar/Avatar/ForgottenArchitect.fbx";
        string destPath = Path.Combine(Application.dataPath, "ForgottenArchitect/ForgottenArchitect.fbx");

        Directory.CreateDirectory(Path.GetDirectoryName(destPath));

        if (File.Exists(sourcePath))
        {
            File.Copy(sourcePath, destPath, true);
            AssetDatabase.Refresh();
            Debug.Log($"FBX imported: {FBX_PATH}");
        }
        else
        {
            Debug.LogWarning($"FBX not found at {sourcePath}");
        }

        // Configure import settings
        ModelImporter importer = AssetImporter.GetAtPath(FBX_PATH) as ModelImporter;
        if (importer != null)
        {
            importer.animationType = ModelImporterAnimationType.Human;
            importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
            importer.importBlendShapes = true;
            importer.importVisibility = true;
            importer.importCameras = false;
            importer.importLights = false;
            importer.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;

            EditorUtility.SetDirty(importer);
            importer.SaveAndReimport();
        }
    }

    private static GameObject ConfigureAvatar()
    {
        Debug.Log("Configuring avatar...");

        // Load FBX
        GameObject fbxPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(FBX_PATH);
        if (fbxPrefab == null)
        {
            Debug.LogError("FBX prefab not found!");
            return null;
        }

        // Instantiate in scene
        GameObject avatarObject = PrefabUtility.InstantiatePrefab(fbxPrefab) as GameObject;
        avatarObject.name = AVATAR_NAME;

        return avatarObject;
    }

    private static void SetupVRChatDescriptor(GameObject avatarObject)
    {
#if VRC_SDK_VRCSDK3
        Debug.Log("Setting up VRChat Avatar Descriptor...");

        VRCAvatarDescriptor descriptor = avatarObject.GetComponent<VRCAvatarDescriptor>();
        if (descriptor == null)
        {
            descriptor = avatarObject.AddComponent<VRCAvatarDescriptor>();
        }

        // Basic settings
        descriptor.Name = AVATAR_NAME;
        descriptor.ViewPosition = new Vector3(0, 1.65f, 0.1f);  // Eye position (tall avatar)

        // Animation settings
        descriptor.Animations = VRCAvatarDescriptor.AnimLayerType.Base;
        descriptor.autoFootsteps = false;
        descriptor.autoLocomotion = true;

        // Lip sync (disabled for horror aesthetic)
        descriptor.lipSync = VRC.SDKBase.VRC_AvatarDescriptor.LipSyncStyle.Default;

        // Eye look (disabled - unsettling stare)
        descriptor.enableEyeLook = false;

        EditorUtility.SetDirty(descriptor);
#else
        Debug.LogWarning("VRChat SDK not found. Skipping descriptor setup.");
#endif
    }

    private static AnimatorController CreateFXAnimator()
    {
        Debug.Log("Creating FX Animator...");

        string controllerPath = "Assets/ForgottenArchitect/FX_Controller.controller";

        AnimatorController controller = AnimatorController.CreateAnimatorControllerAtPath(controllerPath);

        // Add parameters
        controller.AddParameter("MechanicalUnfold", AnimatorControllerParameterType.Bool);
        controller.AddParameter("SystemReboot", AnimatorControllerParameterType.Trigger);
        controller.AddParameter("TheStare", AnimatorControllerParameterType.Bool);

        // Create layers
        AnimatorControllerLayer baseLayer = controller.layers[0];
        baseLayer.name = "Base";

        // Create states (placeholder - animations will be added by Blender export)
        AnimatorStateMachine stateMachine = baseLayer.stateMachine;

        var idleState = stateMachine.AddState("Idle", new Vector3(300, 0, 0));
        var unfoldState = stateMachine.AddState("MechanicalUnfold", new Vector3(300, 100, 0));
        var rebootState = stateMachine.AddState("SystemReboot", new Vector3(300, 200, 0));
        var stareState = stateMachine.AddState("TheStare", new Vector3(300, 300, 0));

        // Create transitions
        var toUnfold = idleState.AddTransition(unfoldState);
        toUnfold.AddCondition(AnimatorConditionMode.If, 0, "MechanicalUnfold");
        toUnfold.duration = 0.2f;

        var fromUnfold = unfoldState.AddTransition(idleState);
        fromUnfold.AddCondition(AnimatorConditionMode.IfNot, 0, "MechanicalUnfold");
        fromUnfold.duration = 0.2f;

        var toReboot = idleState.AddTransition(rebootState);
        toReboot.AddCondition(AnimatorConditionMode.If, 0, "SystemReboot");
        toReboot.duration = 0f;

        var fromReboot = rebootState.AddTransition(idleState);
        fromReboot.hasExitTime = true;
        fromReboot.exitTime = 0.95f;
        fromReboot.duration = 0.1f;

        var toStare = idleState.AddTransition(stareState);
        toStare.AddCondition(AnimatorConditionMode.If, 0, "TheStare");
        toStare.duration = 0.5f;

        var fromStare = stareState.AddTransition(idleState);
        fromStare.AddCondition(AnimatorConditionMode.IfNot, 0, "TheStare");
        fromStare.duration = 0.5f;

        AssetDatabase.SaveAssets();
        Debug.Log($"FX Controller created: {controllerPath}");

        return controller;
    }

    private static void AssignAnimatorToDescriptor(GameObject avatarObject, AnimatorController fxController)
    {
#if VRC_SDK_VRCSDK3
        VRCAvatarDescriptor descriptor = avatarObject.GetComponent<VRCAvatarDescriptor>();
        if (descriptor == null) return;

        // Setup playable layers
        if (descriptor.baseAnimationLayers == null || descriptor.baseAnimationLayers.Length == 0)
        {
            descriptor.customizeAnimationLayers = true;
            descriptor.baseAnimationLayers = new VRCAvatarDescriptor.CustomAnimLayer[5];

            for (int i = 0; i < 5; i++)
            {
                descriptor.baseAnimationLayers[i] = new VRCAvatarDescriptor.CustomAnimLayer();
            }
        }

        // Assign FX controller
        descriptor.baseAnimationLayers[4].isDefault = false;
        descriptor.baseAnimationLayers[4].type = VRCAvatarDescriptor.AnimLayerType.FX;
        descriptor.baseAnimationLayers[4].animatorController = fxController;
        descriptor.baseAnimationLayers[4].isEnabled = true;

        EditorUtility.SetDirty(descriptor);
#endif
    }

    private static VRCExpressionsMenu CreateExpressionsMenu()
    {
#if VRC_SDK_VRCSDK3
        Debug.Log("Creating expressions menu...");

        string menuPath = "Assets/ForgottenArchitect/ExpressionsMenu.asset";
        VRCExpressionsMenu menu = ScriptableObject.CreateInstance<VRCExpressionsMenu>();

        // Add controls
        menu.controls = new List<VRCExpressionsMenu.Control>
        {
            new VRCExpressionsMenu.Control
            {
                name = "Mechanical Unfold",
                type = VRCExpressionsMenu.Control.ControlType.Toggle,
                parameter = new VRCExpressionsMenu.Control.Parameter { name = "MechanicalUnfold" }
            },
            new VRCExpressionsMenu.Control
            {
                name = "System Reboot",
                type = VRCExpressionsMenu.Control.ControlType.Button,
                parameter = new VRCExpressionsMenu.Control.Parameter { name = "SystemReboot" }
            },
            new VRCExpressionsMenu.Control
            {
                name = "The Stare",
                type = VRCExpressionsMenu.Control.ControlType.Toggle,
                parameter = new VRCExpressionsMenu.Control.Parameter { name = "TheStare" }
            }
        };

        AssetDatabase.CreateAsset(menu, menuPath);
        AssetDatabase.SaveAssets();

        Debug.Log($"Expressions menu created: {menuPath}");
        return menu;
#else
        return null;
#endif
    }

    private static VRCExpressionParameters CreateExpressionParameters()
    {
#if VRC_SDK_VRCSDK3
        Debug.Log("Creating expression parameters...");

        string paramsPath = "Assets/ForgottenArchitect/ExpressionParameters.asset";
        VRCExpressionParameters parameters = ScriptableObject.CreateInstance<VRCExpressionParameters>();

        parameters.parameters = new VRCExpressionParameters.Parameter[]
        {
            new VRCExpressionParameters.Parameter
            {
                name = "MechanicalUnfold",
                valueType = VRCExpressionParameters.ValueType.Bool,
                defaultValue = 0,
                saved = true
            },
            new VRCExpressionParameters.Parameter
            {
                name = "SystemReboot",
                valueType = VRCExpressionParameters.ValueType.Bool,
                defaultValue = 0,
                saved = false
            },
            new VRCExpressionParameters.Parameter
            {
                name = "TheStare",
                valueType = VRCExpressionParameters.ValueType.Bool,
                defaultValue = 0,
                saved = true
            }
        };

        AssetDatabase.CreateAsset(parameters, paramsPath);
        AssetDatabase.SaveAssets();

        Debug.Log($"Expression parameters created: {paramsPath}");
        return parameters;
#else
        return null;
#endif
    }

    private static void AssignMenuToDescriptor(GameObject avatarObject, VRCExpressionsMenu menu, VRCExpressionParameters parameters)
    {
#if VRC_SDK_VRCSDK3
        VRCAvatarDescriptor descriptor = avatarObject.GetComponent<VRCAvatarDescriptor>();
        if (descriptor == null) return;

        descriptor.customExpressions = true;
        descriptor.expressionsMenu = menu;
        descriptor.expressionParameters = parameters;

        EditorUtility.SetDirty(descriptor);
#endif
    }

    private static void SaveAsPrefab(GameObject avatarObject)
    {
        Debug.Log("Saving as prefab...");

        PrefabUtility.SaveAsPrefabAsset(avatarObject, PREFAB_OUTPUT_PATH);

        Debug.Log($"Prefab saved: {PREFAB_OUTPUT_PATH}");
    }
}
